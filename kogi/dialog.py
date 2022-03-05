from .utils import han2zen, listfy

VOCAB = {
    '型': 'クラス',
    'クラス': '型',
    'オブジェクト': '値',
    'for文などで': '',
}


def simplify(s):
    ss = [x.split('}')[0] for x in s.split('{') if '}' in x]
    for x in ss:
        if x not in VOCAB:
            VOCAB[x] = x
    return s.format(**VOCAB)

# 用語解説


DESC = {
    'コーギー': 'プログラミング学習を補助してくれるAI犬',
    'プログラミング': '避けては通れない道',
    'データフレーム': 'Pandasで用いられる表データ',
    'イテラブル': '{for文などで}繰り返し処理ができる{オブジェクト}',
}


def response_desc(s, return_html=True):
    if s in DESC:
        desc = listfy(DESC[s])
        desc[0] = simplify(desc[0]) + 'だよ。'
        return desc
    return 'わん'


PYTHON_SIMPLENAME = {
    'NoneType': 'None',
    'bool': '論理値',
    'int': '整数',
    'float': '浮動小数点数',
    'complex': '複素数',
    'str': '文字列',
    'bytes': 'バイト列',
    'list': 'リスト',
    'tuple': '組',
    'dict': '辞書',
    'set': 'セット',
    'ndarray': '配列',
    'DataFrame': 'データフレーム',
    'module': 'モジュール',
    'builtin_function_or_method': 'ビルトイン関数',
    'function': '関数',
    'type': '型もしくはクラス',
}


def render(s, type='type', return_html=True):
    if not return_html:
        return s
    if type.startswith('type'):
        return f'<span class="type">{s}</span>'
    return f'<b style="color: #c3c; font-family: monospace;">{s}</b>'


def typename(value, detail=False):
    if detail:
        ss = [typename(value, detail=False)]
        if hasattr(value, '__next__'):
            ss.append('イテラブル')
        return ', '.join(ss)
    else:
        tyname = type(value).__name__
        if tyname in PYTHON_SIMPLENAME:
            return PYTHON_SIMPLENAME[tyname]
        return tyname + simplify('{クラス}')


def response_value(frame, return_html=True):
    v = frame['value']
    code = render(frame['code'], 'code', return_html=return_html)
    tyname = render(typename(v), 'type', return_html=return_html)
    if return_html and hasattr(v, '_repr_html_'):
        return [f'{code}の型は{tyname}。値は以下のとおり。', v._repr_html_()]
    if hasattr(v, '__len__') and len(v) > 100:
        value = render(str(v[:100]), 'value',
                       return_html=return_html) + '...(以下、省略)'
    else:
        value = render(repr(v), 'value', return_html=return_html)
    return f'{code}の型は、{tyname}。値は{value}'


def response_whatis(text, frame, return_html=True):
    try:
        v = get_ipython().ev(text)
        frame['code'] = text
        frame['value'] = v
    except:
        pass
    if 'value' in frame:
        return response_value(frame, return_html=return_html)
    return response_desc(text, return_html=return_html)


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


def response_simply(text, frame):
    text = han2zen(text)
    text = remove_tails(text)
    if text.endswith('には'):
        text = text[:-2]
        return 'TODO: コード翻訳するよ！'
    if text.endswith('って') or text.endswith('とは'):
        text = text[:-2]
        return response_whatis(text, frame)
    if text.startswith('原因') or text.startswith('理由'):
        if 'reason' in frame:
            return frame['reason']
        else:
            return 'わん'
    if text.startswith('解決') or text.startswith('どう'):
        if 'solution' in frame:
            return frame['solution']
        else:
            if 'reason' in frame:
                return '原因を特定してみてね'
            return 'ググってみたら'
    if text.startswith('ヒント'):
        if 'hint' in frame:
            return frame['hint']
        else:
            return 'ノー ヒント！'
    return response_whatis(text, frame)


def get_chatbot():
    return response_simply


if __name__ == '__main__':
    # テストはここに
    print(response_desc('イテラブル'))
    frame = {'code': 'df', 'value': 's'}
    print(response_value(frame))
    frame = {'code': '1+1'}
    print(response_simply('プログラミングするには', frame))
