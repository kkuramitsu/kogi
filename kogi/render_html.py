

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


# HTML render

def render(s: str, type='type', render_html=True) -> str:
    if type.startswith('type'):
        s = PYTHON_SIMPLENAME.get(s, f'{s}型')
    if not render_html:
        return s
    if type.startswith('type'):
        return f'<span class="type">{s}</span>'
    return f'<b style="color: #c3c; font-family: monospace;">{s}</b>'


def render_astype(value: object, render_html=True) -> str:
    return render(type(value).__name__, 'type', render_html=render_html)


def render_value(value: object, render_html=True) -> str:
    if not render_html:
        return str(value)
    if hasattr(value, '_repr_html_'):
        return value._repr_html_()
    if hasattr(value, '__len__') and len(value) > 8:
        return render(str(value[:8]), 'value', render_html=render_html) + '...(以下、省略)'
    return render(repr(value), 'value', render_html=render_html)
