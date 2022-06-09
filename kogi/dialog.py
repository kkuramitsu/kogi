import sys
import traceback
import requests

from kogi.liberr import catch_exception
from .utils import listfy, zen2han, remove_suffixes
from .logger import send_log, kogi_print, send_slack, print_nop

DUMMY = 'rhOcswxkXzMbhlkKQJfytbfxAPVsblhRHX'

REMOVED_SUFFIXES = [
    '.', '。', '?', '？', '！',
    '何', '何ですか', '何でしょうか',
    'が知りたい', 'がしりたい', 'がわからない', 'が分からない',
]


def startswith(text, prefixes):
    for prefix in prefixes:
        if text.startswith(prefix):
            return True
    return False


def remove_tai(s):
    if s.endswith('したい'):
        return s[:-3]+'する'
    if s.endswith('きたい'):
        return s[:-3]+'く'
    if s.endswith('ちたい'):
        return s[:-3]+'つ'
    if s.endswith('にたい'):
        return s[:-3]+'ぬ'
    if s.endswith('りたい'):
        return s[:-3]+'る'
    if s.endswith('みたい'):
        return s[:-3]+'む'
    if s.endswith('いたい'):
        return s[:-3]+'う'
    if s.endswith('ぎたい'):
        return s[:-3]+'ぐ'
    if s.endswith('びたい'):
        return s[:-3]+'ぶ'
    return s[:-2]+'る'


HINT = {
    'abc231_a': '難しいことはありません.',
    #
    'abc220_a': 'ここで、range()の使い方をマスターしましょう',
    'abc165_b': '誤差が生じないように整数で計算します',
    'abc192_b': 'for i, c in enumerate(S): のように、enumerate()を使ってみよう',
    'abc184_b': 'シミュレーションして１問ずつ得点を計算します',
    'abc194_b': '要するに、argmin()。優秀な人は二人分仕事しても早いので注意',
    'abc186_c': '8進数文字に変換してみたら？',

    # 関数
    'abc183_a': 'ReLUはランプ関数と呼びます。AIでは定番の関数です。ぜひ関数定義してから計算しましょう.',
    'abc234_a': 'Pythonの関数定義を思い出して、f(x)を定義してから計算します',
    'abc220_b': 'K進法表記の文字列を整数に変換する方法を探してみましょう',
    'abc083_b': '各桁の和は、文字列に変換して、数字として計算するといいですよ',
    'abc229_b': '順序を入れ替えて１の位を数列の先頭にします。\nfor a, b in zip(A, B)のようにzipを使ってみましょう。',
    'abc192_c': '関数g1(x), g2(x), f(x)を順番に定義し、0からkまで順番に計算します。これができたら、繰り返しと関数はマスター！',
    'abc227_b': '変数a,bのとりうる範囲を二重ループで全探索し、全ての面積を列挙します。\nリストの代わりにセット(set)を使ってみましょう',

    'abc222_b': 'リストへは、a=list(map(int, input().split()))のように読み込みます',
    'abc204_b': 'numpyを使うとスッキリかけます',

    'abc218_b': '整数値を文字コードにシフトさせて、chr()で文字に変換します',
    'abc188_b': 'ループを計算しても構いませんが、numpyを使っても良いです',
    'abc188_b': '新しいリストに追加すると簡単。もちろん。numpyを使っても良いです',
    'abc210_b': '坊主めくりをシミュレーションしましょう',
    'abc188_c': '完全二分木において、準優勝するとはどう言うことか考えましょう',
}

# コード翻訳

code_nmt = None


def kogi_set_codenmt(nmt_fn):
    global code_nmt
    code_nmt = nmt_fn


def response_codenmt(text: str, slots: dict):
    global code_nmt
    if code_nmt is None:
        return 'わん'
    return code_nmt(text)


class Chatbot(object):
    slots: dict

    def __init__(self, slots=None):
        self.slots = {} if slots is None else slots

    def get(self, key, value=''):
        return self.slots.get(key, value)

    def response(self, text):
        text = zen2han(text)
        text = remove_suffixes(text, REMOVED_SUFFIXES)
        if startswith(text, ('デバッグ', '助けて', 'たすけて', '困った', '変数')):
            if 'fault_vars' in self.slots:
                return self.slots['fault_vars']
            else:
                return 'コギーもお手上げ..'
        if text.endswith('には'):
            text = text[:-2]
            return response_codenmt(text, self.slots)
        if text.endswith('たい'):
            text = remove_tai(text)
            return response_codenmt(text, self.slots)
        if text.endswith('って') or text.endswith('とは'):
            text = text[:-2]
            return self.response_desc(text)
        if startswith(text, ('ヒント', '助けて', 'たすけて')):
            if 'hint' in self.slots:
                return self.slots['hint']
            else:
                return 'うーん'
        if startswith(text, ('原因', '理由', 'なぜ', 'なんで', 'どうして')):
            if 'reason' in self.slots:
                return self.slots['reason']
            else:
                return self.response_vow(text)
        if startswith(text, ('解決', 'どう', 'お手上げ')):
            if 'solution' in self.slots:
                return self.slots['solution']
            elif 'hint' in self.slots:
                return self.slots['hint']
            elif 'reason' in self.slots:
                return self.slots['reason']
            return self.response_vow(text)
        return self.response_code(text)

    def response_vow(self, text):
        return "わん"

    def response_translate(self, text):
        return response_translate(text)

    def response_desc(self, text):
        return response_translate(text)

    def response_variables(self, name=None):
        ss = ['変数を全部、表示するよ']
        for stack in self.get('stacks'):
            if 'vars' not in stack:
                continue
            vars = stack['vars']
            if name is None:
                for n in vars.keys():
                    if n.startswith('_') or n in SKIP_IDS:
                        continue
                    v = vars[n]
                    ty = type(v).__name__
                    if ty in ('module', 'function'):
                        continue
                    ss.append(render_value(n, ty, vars[n]))
            elif name in vars:
                v = vars[name]
                ss.append(render_value(name, type(v).__name__, v))
        return ss

    def response_code(self, text):
        return self.response_vow(text)


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


SKIP_IDS = set([
    'In', 'Out', 'get_ipython', 'exit', 'quit'
])


def render_value(name, typename, value):
    head = f'<b>{name}: {typename}型</b>'
    if hasattr(value, '__len__'):
        v = len(value)
        head += f' <tt>len({name})={v}</tt>'
    body = f'<pre>{repr(value)}</pre>'
    if hasattr(value, '_repr_html_'):
        body = value._repr_html_()
    return f'{head}<br/>{body}'


# 分析

_PYTYPE = {
    'NoneType': 'None',
    'bool': 'ブール値',
    'int': '整数',
    'float': '浮動小数点数',
    'complex': '複素数',
    'str': '文字列',
    'bytes': 'バイト列',
    'list': 'リスト',
    'tuple': 'タプル',
    'dict': '辞書',
    'set': 'セット',
    'ndarray': '配列',
    'DataFrame': '表データ/データフレーム',
    'module': 'モジュール',
    'builtin_function_or_method': '関数/ビルトイン関数',
    'function': '関数',
    'type': '型もしくはクラス',
}


def _typename(value):
    typename = type(value).__name__
    if typename in _PYTYPE:
        return _PYTYPE[typename] + f'({typename}型)'
    return f'{typename}型'


def dump_value(key, value):
    ss = []
    ss.append(key)
    ss.append(_typename(value))
    if hasattr(value, '__len__'):
        ss.append(f'len({key})={len(value)}')
    ss.append(str(value))
    return ' '.join(ss)


def thinking(slots, print=kogi_print):
    # print(slots)
    if 'code' in slots and 'traceback' in slots:
        code = slots['code']
        lines = []
        for data in slots['traceback']:
            lineno = data['lineno']
            line = data['line'].strip()
            if line in code:
                line = f'{line} [{lineno}行目]に変なところない？'
                lines.append(line)
                print(line)
        if len(lines) > 0:
            slots['fault_lines'] = lines
    if 'vars' in slots:
        if len(slots['vars']) > 0:
            fault_vars = ['変数の値を全部、出してみるよ（変な値はないか探してごらん)']
            print(fault_vars[0])
            for key, value in slots['vars'].items():
                dump = dump_value(key, value)
                fault_vars.append(dump)
            slots['fault_vars'] = fault_vars
    if 'problem_id' in slots:
        text = slots['problem_id']
        if text in HINT:
            text = HINT[text]
            slots['hint'] = text
            print(f'ヒント: {text}')
    if 'reason' in slots:
        text = slots['reason']
        print(f'原因: たぶん{text}')
    else:
        if 'fault_lines' in slots:
            slots['reason'] = slots['fault_lines'][0]
        else:
            slots['reason'] = f'原因: たぶん... わん（犬に戻りました）'
    if 'solution' in slots:
        text = slots['solution']
        print(f'解決策: たぶん{text}')
    else:
        slots['solution'] = f'解決策は... (次のバージョン更新をお待ちください）'


# コントローラ
try:
    from google.colab import output

    def _start_chat(chatbot, start_message):
        from IPython.display import display, HTML
        from .dialog_html import BOT_ICON, BOT_HTML, CLEAR_HTML, YOUR_ICON, USER_HTML, CHAT_CSS, CHAT_HTML

        def _display_bot(bot_text):
            with output.redirect_to_element('#output'):
                bot_name = chatbot.get('bot_name', 'コギー')
                bot_icon = chatbot.get('bot_icon', BOT_ICON)
                for text in listfy(bot_text):
                    text = text.replace('\n', '<br/>')
                    display(HTML(BOT_HTML.format(bot_icon, bot_name, text)))
            if 'バイバイ' in bot_text:
                display(HTML(CLEAR_HTML))

        def _display_you(your_text):
            with output.redirect_to_element('#output'):
                your_name = chatbot.get('your_name', 'あなた')
                your_icon = chatbot.get('your_icon', YOUR_ICON)
                for text in listfy(your_text):
                    text = text.replace('\n', '<br/>')
                    display(HTML(USER_HTML.format(your_icon, your_name, text)))

        def debug_log():
            try:
                send_log()
            except Exception as e:
                print(e)

        # Display main
        display(HTML(CHAT_CSS))
        display(HTML(CHAT_HTML))

        def ask(your_text):
            your_text = your_text.strip()
            if 'ありがとう' in your_text or 'バイバイ' in your_text:
                display(HTML(CLEAR_HTML))
            try:
                _display_you(your_text)
                bot_text = chatbot.response(your_text)
                if bot_text is not None:
                    _display_bot(bot_text)
            except Exception as e:
                _display_bot('バグりました。\nご迷惑をおかけします。')
                traceback.print_exc()

        output.register_callback('notebook.ask', ask)
        output.register_callback('notebook.log', debug_log)

        send_log(right_now=True)
        _display_bot(start_message)

except:  # Colab 上ではない

    def _start_chat(chatbot, start_message):
        try:
            bot_text = start_message
            bot_name = chatbot.get('bot_name', 'コギー')
            kogi_print(bot_text)
        except:
            kogi_print('バグりました。ご迷惑をおかけします')
            traceback.print_exc()

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
    thinking(dialog_slots, print=kogi_print)
    chatbot = Chatbot(slots=dialog_slots)
    if 'translated' in dialog_slots:
        _start_chat(chatbot, dialog_slots['translated'])
    else:
        kogi_print('コギーは、未知のエラーに驚いた（みんながいじめるので隠れた）')
        send_slack(slots)


def kogi_catch(exc_info=None, code: str = None, context: dict = None, enable_dialog=True, logging_json=None):
    if exc_info is None:
        exc_info = sys.exc_info()
    slots = catch_exception(exc_info, code=code, logging_json=logging_json)
    if context is not None:
        slots.update(context)
    if enable_dialog:
        start_dialog(slots, logging_json=logging_json)


if __name__ == '__main__':
    start_dialog({})
