import sys
import traceback
import requests
from IPython import get_ipython
from kogi.diagnosis import run_diagnosis

try:
    from google.colab import output
except ModuleNotFoundError:
    output = None

from kogi.ui import kogi_display, display_dialog, Conversation

from kogi.liberr import kogi_print_exc

from .nmt import kogi_nmt_talk, kogi_nmt_wakeup
import kogi.fake_nlp as nlp

from .logger import send_log, kogi_print, send_slack, print_nop

DUMMY = 'rhOcswxkXzMbhlkKQJfytbfxAPVsblhRHX'


# コード翻訳

def repr_liner(ss):
    ss2 = []
    for s in ss:
        if s not in ss2:
            ss2.append(s)
    return '<br>'.join(f'<code>{s}</code>' for s in ss2)


def response_codenmt(text: str, slots: dict):
    res = kogi_nmt_talk(text, beam=5)
    if res is not None:
        results, scores = res
        #print(results, scores)
        return repr_liner(results)
    return 'コギーは、眠む眠む..'


def response_talknmt(text: str, slots: dict):
    res = kogi_nmt_talk(f'talk: {text}', beam=1)
    if res is not None:
        return res
    return 'コギーは、眠む眠む..'


API_URL = "https://api-inference.huggingface.co/models/kkuramitsu/kogi-mt5-test"
headers = {"Authorization": f"Bearer hf_{DUMMY}"}


def response_translate(text):
    if len(text) > 80:
        return 'ぐるるるる\n（入力が長すぎます）'
    payload = {"inputs": text}
    response = requests.post(API_URL, headers=headers, json=payload)
    output = response.json()
    print(text, type(output), output)
    if isinstance(output, (list, tuple)):
        output = output[0]
    if 'generated_text' in output:
        return output['generated_text']
    return 'ねむねむ。まだ、起きられない！\n（しばらく待ってからもう一度試してください）'


class Chatbot(Conversation):

    def response(self, user_input):
        text = user_input
        if 'user_inputs' not in self.slots:
            self.slots['user_inputs'] = []
        self.slots['user_inputs'].append(text)
        if nlp.startswith(text, ('質問')):
            return self.response_question(text)
        if nlp.startswith(text, ('起き', '寝るな', '寝ない')):
            kogi_display('あと１分！')
            kogi_nmt_wakeup()
            return 'おはようございます'
        text = nlp.normalize(user_input)
        if nlp.startswith(text, ('デバッグ', '助けて', 'たすけて', '困った', '分析', '調べて')):
            if 'fault_vars' in self.slots:
                return self.slots['fault_vars']
            else:
                return 'コギーも助けて...'
        if text.endswith('には'):
            text = text[:-2]
            return response_codenmt(text, self.slots)
        if text.endswith('たい'):
            text = nlp.remove_tai(text)
            return response_codenmt(text, self.slots)
        if text.endswith('って') or text.endswith('とは'):
            text = text[:-2]
            return self.response_desc(text)
        if nlp.startswith(text, ('原因', '理由', 'なぜ', 'なんで', 'どうして', 'どして')):
            if 'reason' in self.slots:
                return self.slots['reason']
            if 'fault_lines' in self.slots:
                return self.slots['fault_lines']
            return 'エラーメッセージから考えてみよう'
        if nlp.startswith(text, ('解決', 'どう', 'お手上げ', 'ヒント')):
            if 'solution' in self.slots:
                return self.slots['solution']
            if 'maybe' in self.slots:
                return 'ひょっとしたら、' + self.slots['maybe']
            return 'きゅるるる...'
        if nlp.startswith(text, ('ヒント', '助けて', 'たすけて')):
            if 'hint' in self.slots:
                return self.slots['hint']
            else:
                return 'ヒントなし'
        return response_talknmt(text, self.slots)

    def response_question(self, text):
        send_slack(dict(
            type='dialog_question',
            text=text,
            context=self.slots,
        ))
        return 'わん！わん！わん！ 先生を呼んでみました'

    def response_desc(self, text):
        send_slack(dict(
            type='dialog_desc',
            code=self.slots.get('code', ''),
            text=text,
        ))
        return 'コギーの苦手な内容だから、TAさんに質問を転送したよ'

    def response_vow(self, text):
        return "わん"

    def response_code(self, text):
        return self.response_vow(text)


if output is None:

    def show_slots(slots, print=kogi_display):
        if 'reason' in slots:
            print(slots['reason'])
        if 'fault_lines' in slots:
            for reason in slots['fault_lines']:
                print(reason)
        if 'solution' in slots:
            print(slots['solution'])
        if 'maybe' in slots:
            print(slots['maybe'])
        if 'fault_vars' in slots:
            for reason in slots['fault_vars']:
                print(reason)
        if 'hint' in slots:
            print(slots['hint'])

    def _start_chat(chatbot, start_message):
        try:
            chatbot.get('bot_name', 'コギー')
            kogi_display(start_message)
            show_slots(chatbot.slots)
        except:
            kogi_print('バグりました。ご迷惑をおかけします')
            traceback.print_exc()

    def _start_chat(chatbot, start_message):
        bot, _ = display_dialog(chatbot)
        bot(start_message)

else:
    def _start_chat(chatbot, start_message):
        bot, _ = display_dialog(chatbot)
        bot(start_message)


global_slots = {
    'bot_name': 'コギー',
    'your_name': 'あなた',
}


def set_global_slots(**kwargs):
    for key, value in kwargs.items():
        global_slots[key] = value


def start_dialog(slots: dict, logging_json=None):
    dialog_slots = global_slots.copy()
    dialog_slots.update(slots)
    chatbot = Chatbot(slots=dialog_slots)
    if 'translated' in dialog_slots:
        _start_chat(chatbot, dialog_slots['translated'])
    else:
        kogi_display('コギーは、未知のエラーに驚いた（みんながいじめるので隠れた）')
        if logging_json is not None:
            slots['type'] = 'unknown_emsg'
            print(slots)
            logging_json(**slots)


def kogi_catch(exc_info=None, code: str = None, context: dict = None, exception=None, enable_dialog=True, logging_json=None):
    if exc_info is None:
        exc_info = sys.exc_info()
    slots = kogi_print_exc(code=code, exc_info=exc_info,
                           exception=exception, logging_json=logging_json)
    if context is not None:
        slots.update(context)
    run_diagnosis(slots)
    if enable_dialog:
        start_dialog(slots, logging_json=logging_json)


if __name__ == '__main__':
    start_dialog({})
