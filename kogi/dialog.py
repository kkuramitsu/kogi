from .utils import zen2han, listfy
from .render_html import render, render_value, render_astype
from .dialog_desc import response_desc
from .nmt import get_nmt

# VOCAB = {
#     '型': 'クラス',
#     'クラス': '型',
#     'オブジェクト': '値',
#     'for文などで': '',
# }


# def simplify(s):
#     ss = [x.split('}')[0] for x in s.split('{') if '}' in x]
#     for x in ss:
#         if x not in VOCAB:
#             VOCAB[x] = x
#     return s.format(**VOCAB)

REMOVED = [
    '.', '。', '?', '？', '！',
    '何', '何ですか', '何でしょうか',
    'が知りたい', 'がしりたい', 'がわからない', 'が分からない',
]


def remove_tails(s):
    for suffix in REMOVED:
        if s.endswith(suffix):
            return remove_tails(s[:-len(suffix)])
    return s


def get_global_frame():
    return {}


class Chatbot(object):
    frame: dict
    render_html: bool

    def __init__(self, frame=None, render_html=True):
        self.frame = {} if frame is None else frame
        self.frame.update(get_global_frame())
        self.render_html = render_html
        self.nmt = get_nmt()

    def response(self, text):
        text = zen2han(text)
        text = remove_tails(text)
        if text.endswith('には'):
            text = text[:-2]
            return self.response_translate(text)
        if text.endswith('って') or text.endswith('とは'):
            text = text[:-2]
            return self.response_desc(text)
        if text.startswith('原因') or text.startswith('理由'):
            if 'reason' in self.frame:
                return self.frame['reason']
            else:
                return self.response_vow(text)
        if text.startswith('解決') or text.startswith('どう'):
            if 'solution' in self.frame:
                return self.frame['solution']
            else:
                if 'reason' in self.frame:
                    return '原因を特定してみてね'
                return 'ググってみたら'
        if text.startswith('ヒント'):
            if 'hint' in self.frame:
                return self.frame['hint']
            else:
                return 'ノー ヒント！'
        return self.response_code(text)

    def response_translate(self, text):
        return self.nmt(f'trans: {text}')

    def response_desc(self, text):
        return response_desc(text)

    def response_code(self, text):
        try:
            v = get_ipython().ev(text)
            self.frame['code'] = text
            self.frame['value'] = v
        except:
            pass
        if 'value' not in self.frame:
            return self.response_vow(text)
        code = render(text, 'code', render_html=self.render_html)
        tyname = render_astype(v, render_html=self.render_html)
        value = render_value(v, render_html=self.render_html)
        return [f'{code}の型は{tyname}。値は', value]

    def response_vow(self, text):
        return self.nmt(f'talk: {text}')


def get_chatbot(frame=None):
    chatbot = Chatbot(frame=frame)
    return lambda text: chatbot.response(text)


if __name__ == '__main__':
    chat = get_chatbot()
    print(chat('イテラブルとは'))
