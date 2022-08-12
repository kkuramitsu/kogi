import traceback
from .content import ICON, JS, CSS
from IPython.display import display, HTML
from kogi.settings import translate_ja, kogi_get

try:
    from google.colab import output
except ModuleNotFoundError:
    output = None

APPEND_JS = '''
<script>
var target = document.getElementById('{target}');
var content = `{html}`;
if(target !== undefined) {{
    target.insertAdjacentHTML('beforeend', content);
    target.scrollTop = target.scrollHeight;
}}
</script>
'''


def append_content(target, html):
    html = html.replace('\\', '\\\\')
    html = html.replace('`', '\\`')
    display(HTML(APPEND_JS.format(target=target, html=html)))


DIALOG_BOT_HTML = '''
<div class="sb-box">
    <div class="icon-img icon-img-left">
        <img src="{icon}" width="60px">
    </div>
    <div class="icon-name icon-name-left">{name}</div>
    <div class="sb-side sb-side-left">
        <div class="sb-txt sb-txt-left">{text}</div>
    </div>
</div>
'''

DIALOG_USER_HTML = '''
<div class="sb-box">
    <div class="icon-img icon-img-right">
        <img src="{icon}" width="60px">
    </div>
    <div class="icon-name icon-name-right">{name}</div>
    <div class="sb-side sb-side-right">
        <div class="sb-txt sb-txt-right">{text}</div>
    </div>
</div>
'''

dialog_count = 0
dialog_target = None


def cc(text):
    if len(text)==0:
        return text
    n_ascii = sum(1 for c in text if ord(c) < 128)
    #print(text, n_ascii, len(text), n_ascii / len(text))
    if (n_ascii / len(text)) < 0.4:  # 日本語
        t = translate_ja(text)
        # print(t)
        if t is not None:
            return f'{text}<br><i>{t}</i>'
    return text


def kogi_display(text, **kwargs):
    if isinstance(text, list):
        text = '<br>'.join(cc(line) for line in text)
    else:
        text = cc(text)

    data = dict(
        text=text,
        icon='kogi-fs8.png',
        name='コギー',
    )
    data.update(kwargs)
    data['icon'] = ICON(data.get('icon', '/'))
    _HTML = kwargs.get('html', DIALOG_BOT_HTML)
    html = _HTML.format(**data)
    #print('@@', html, kwargs)
    if dialog_target is not None:
        append_content(dialog_target, html=html)
    else:
        display(HTML(CSS('dialog.css') + html))


DIALOG_HTML = '''
<div id="dialog">
    {script}
    <div id="{target}" class="box" style="height: 150px">
    </div>
    <div style="text-align: right">
        <textarea id="input" placeholder="{placeholder}"></textarea>
    </div>
</div>
'''


class Conversation(object):
    slots: dict
    records: list

    def __init__(self, slots=None):
        self.slots = {} if slots is None else slots
        self.records = []

    def get(self, key, value):
        return self.slots.get(key, value)

    def ask(self, input_text):
        output_text = self.response(input_text)
        self.records.append((input_text, output_text))
        return output_text

    def response(self, input_text):
        return 'わん'


def display_dialog(context=None, placeholder='質問はこちらに'):
    global dialog_target, dialog_count
    dialog_target = f'output{dialog_count}'
    dialog_count += 1
    data = dict(
        script=JS('dialog.js'),
        placeholder=placeholder,
        target=dialog_target,
    )
    DHTML = DIALOG_HTML.replace('150', str(kogi_get('chat_height', 180)))
    display(HTML(CSS('dialog.css') + DHTML.format(**data)))
    if context is None:
        context = Conversation()

    def dialog_bot(bot_text, **kwargs):
        nonlocal context
        data = dict(
            icon=context.get('bot_icon', 'kogi-fs8.png'),
            name=context.get('bot_name', 'コギー'),
        )
        data.update(kwargs)
        kogi_display(bot_text, **data)

    def dialog_user(user_text, **kwargs):
        nonlocal context
        data = dict(
            icon=context.get('user_icon', 'girl_think-fs8.png'),
            name=context.get('user_name', 'あなた'),
            html=DIALOG_USER_HTML,
        )
        data.update(kwargs)
        kogi_display(user_text, **data)

    if output is not None:
        def ask(user_text):
            try:
                user_text = user_text.strip()
                dialog_user(user_text)
                bot_text = context.ask(user_text)
                dialog_bot(bot_text)
                #print('@', bot_text)
            except:
                kogi_display('バグで処理に失敗しました。ごめんなさい')
                traceback.print_exc()
        output.register_callback('notebook.ask', ask)

    return dialog_bot, dialog_user
