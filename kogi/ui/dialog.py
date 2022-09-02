import traceback
from .content import ICON, JS, CSS
from ._google import google_colab

from IPython.display import display, HTML
from kogi.settings import translate_ja, isEnglishDemo

def cc(text):
    if isEnglishDemo():
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

def htmlfy(text):
    if isinstance(text, list):
        text = '<br>'.join(cc(line) for line in text)
    else:
        text = cc(text)
    return text


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

def htmlfy_bot(chat, text):
    return DIALOG_BOT_HTML.format(
        icon=ICON(chat.get('bot_icon', 'kogi-fs8.png')),
        name=chat.get('bot_name', 'コギー'),
        text=htmlfy(text)
    )


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

def htmlfy_user(chat, text):
    return DIALOG_USER_HTML.format(
        icon=ICON(chat.get('user_icon', 'girl_think-fs8.png')),
        name=chat.get('name', 'あなた'),
        text=htmlfy(text)
    )
    

DIALOG_ID = 0

class Conversation(object):
    slots: dict
    records: list

    def __init__(self, slots=None):
        global DIALOG_ID
        self.cid= DIALOG_ID
        DIALOG_ID += 1
        self.slots = {} if slots is None else slots
        self.records = []

    def get(self, key, value):
        return self.slots.get(key, value)

    def ask(self, input_text):
        output_text = self.response(input_text)
        self.records.append((input_text, output_text))
        output_text = cc(output_text)
        return output_text

    def response(self, input_text):
        return 'わん'


