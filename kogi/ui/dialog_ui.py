from .content import ICON, JS, CSS
from IPython.display import display, HTML

try:
    from google.colab import output
except ModuleNotFoundError:
    output = None

SCRIPT = '''
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
    html = html.replace('`', '\\`')
    display(HTML(SCRIPT.format(target=target, html=html)))


_DIALOG_BOT = '''
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

_DIALOG_USER = '''
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


def kogi_print(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    data = dict(
        text=sep.join([str(s) for s in args]),
        icon='kogi-fs8.png',
        name='コギー',
    )
    data.update(kwargs)
    data['icon'] = ICON(data.get('icon', '/'))
    _HTML = kwargs.get('html', _DIALOG_BOT)
    html = _HTML.format(**data)
    if 'target' in kwargs:
        target = kwargs['target']
        #print('target', target)
        append_content(target, html=html)
    else:
        display(HTML(CSS('dialog.css') + html))


_DIALOG_MAIN = '''
<div id='dialog'>
    {script}
    <div id='output' class='box'>
    </div>
    <div style='text-align: right'>
        <textarea id='input' placeholder='{placeholder}'></textarea>
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

    def response(self, input_text):
        return 'わん'


def display_dialog(placeholder='質問はこちらに', context=None):
    data = dict(
        script=JS('dialog.js'),
        placeholder=placeholder
    )
    display(HTML(CSS('dialog.css') + _DIALOG_MAIN.format(**data)))
    if context is None:
        context = Conversation()

    def dialog_bot(bot_text, **kwargs):
        nonlocal context
        data = dict(
            icon=context.get('bot_icon', 'kogi-fs8.png'),
            name=context.get('bot_name', 'コギー'),
            target='output'
        )
        data.update(kwargs)
        kogi_print(bot_text, **data)

    def dialog_user(user_text, **kwargs):
        data = dict(
            icon=context.get('user_icon', 'girl_think-fs8.png'),
            name=context.get('user_name', 'あなた'),
            html=_DIALOG_USER,
            target='output'
        )
        data.update(kwargs)
        kogi_print(user_text, **data)

    if output is not None:
        def ask(user_text):
            dialog_user(user_text)
            bot_text = context.ask(user_text)
            dialog_bot(bot_text)
        output.register_callback('notebook.ask', ask)

    return dialog_bot, dialog_user


class Deco(object):

    def bold(self, text):
        return f'<b>{text}</b>'

    def code(self, text):
        return f'<code>{text}</code>'
