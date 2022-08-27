from IPython.display import display
from ipywidgets import Text, HTML
from .content import CSS
from .dialog import htmlfy_bot, htmlfy_user, Conversation


def htmlfy_dialog(chat, records, text=None):
    ss = [CSS('dialog.css')]
    ss.append('<div class="box2">')
    if text:
        records.append(text)
    ss.extend(records)
    ss.append('</div>')
    return ''.join(ss)

def display_dialog(chat, start=None, placeholder='質問はこちらに'):
    records=[]
    if start:
        start = htmlfy_bot(chat, start)
    html=HTML(value=htmlfy_dialog(chat, records, start))
    text = Text(value='',
                placeholder=placeholder,
                description='文字:',
                disabled=False
    )
    
    def dialog_bot(bot_text):
        nonlocal chat, records
        records.append(htmlfy_bot(chat, bot_text))
        html.value=htmlfy_dialog(chat, records)

    def dialog_user(user_text):
        nonlocal chat, records
        records.append(htmlfy_user(chat, user_text))
        html.value=htmlfy_dialog(chat, records)

    def update(submit):
        print(submit.value)
        user_text = str(submit.value).strip()
        dialog_user(user_text)
        bot_text = chat.ask(user_text)
        dialog_bot(bot_text)
        text.value=''

    text.on_submit(update)
    display(html)
    display(text)
    return dialog_bot, dialog_user
