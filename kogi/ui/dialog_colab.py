import traceback
from .content import JS, CSS
from ._google import google_colab

from IPython.display import display, HTML
from kogi.settings import kogi_get
from .dialog import htmlfy_bot, htmlfy_user, Conversation

DIALOG_COLAB_HTML = '''
<div id="dialog">
    {script}
    <div id="{target}" class="box" style="height: 150px">
    </div>
    <div style="text-align: right">
        <textarea id="input" placeholder="{placeholder}"></textarea>
    </div>
</div>
'''

DIALOG_HTML = '''
<div id="dialog">
    {script}
    <div id="{target}" class="box" style="height: 150px">
    </div>
</div>
'''

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

def append_talk(html, dialog_target):
    if dialog_target:
        html = html.replace('\\', '\\\\')
        html = html.replace('`', '\\`')
        display(HTML(APPEND_JS.format(target=dialog_target, html=html)))
    else:
        display(HTML(CSS('dialog.css') + html))

def display_dialog(chat: Conversation, start=None, placeholder='質問はこちらに'):
    dialog_target = f'output{chat.cid}'
    data = dict(
        script=JS('dialog.js'),
        placeholder=placeholder,
        target=dialog_target,
    )
    if google_colab:
        DHTML = DIALOG_COLAB_HTML.replace('150', str(kogi_get('chat_height', 180)))
        display(HTML(CSS('dialog.css') + DHTML.format(**data)))
    else:
        DHTML = DIALOG_HTML.replace('150', str(kogi_get('chat_height', 180)))
        display(HTML(CSS('dialog.css') + DHTML.format(**data)))

    def dialog_bot(bot_text):
        nonlocal chat, dialog_target
        html=htmlfy_bot(chat, bot_text)
        append_talk(html, dialog_target)

    def dialog_user(user_text):
        nonlocal chat, dialog_target
        html=htmlfy_user(chat, user_text)
        append_talk(html, dialog_target)

    if google_colab:
        def ask(user_text):
            try:
                user_text = user_text.strip()
                dialog_user(user_text)
                bot_text = chat.ask(user_text)
                dialog_bot(bot_text)
                #print('@', bot_text)
            except:
                dialog_bot('バグで処理に失敗しました。ごめんなさい')
                traceback.print_exc()
        google_colab.register_callback('notebook.ask', ask)
    if start:
        dialog_bot(start)
    return dialog_bot, dialog_user
