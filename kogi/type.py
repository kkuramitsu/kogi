_PYTYPE = {
    'NoneType': 'None',
    'bool': '論理値',
    'int': '整数',
    'float': '実数/浮動小数点数',
    'complex': '複素数',
    'str': '文字列',
    'bytes': 'バイト列',
    'list': 'リスト',
    'tuple': '組/タプル',
    'dict': '辞書/マッピング',
    'set': '集合/セット',
    'ndarray': '配列/NumPy配列',
    'DataFrame': '表データ/データフレーム',
    'module': 'モジュール',
    'builtin_function_or_method': '関数/ビルトイン関数',
    'function': '関数',
    'type': '型もしくはクラス',
}


def _span(s, css_class, return_html=True):
    if return_html:
        return f'<span class="{css_class}">{s}</span>'
    return s


def _kogi_typename(value, return_html=True):
    typename = type(value).__name__
    if typename in _PYTYPE:
        return _span(_PYTYPE[typename], "type", return_html)
    return _span(typename, "type", return_html) + 'クラス'


def _kogi_typename(type_name, suffix=''):
    if type_name in _PYTYPE:
        return _simple(_PYTYPE[type_name]) + suffix
    else:
        return type_name + _simple('型/クラス')


def _kogi_inspect(v):
    type_name = type(v).__name__
    d = {'typeid': type_name, 'type': _kogi_typename(type_name)}
    if hasattr(v, '__next__'):
        d['iterable'] = hasattr(v, '__next__')
    if hasattr(v, '__len__'):
        d['len'] = len(v)
    if hasattr(v, '__name__'):
        d['name'] = v.__name__
    return d


def _html_symbol(s, return_html=True):
    if return_html:
        return f'<span class="symbol" style="color: #c3c; font-family: monospace;">{s}</span>'
    return s


def _html_value(s, return_html=True):
    if len(s) > 100:
        s = s[:100] + '...(以下、省略)'
    if return_html:
        return f'<span class="value" style="font-family: monospace">{s}</span>'
    return s


def _kogi_say_names(names, msgs, return_html=True):
    for d in names:
        if 'value' in d:
            symbol = _html_symbol(d['id'], return_html=True)
            typename = _html_type(d['type'], return_html=True)
            value = d['value']
            if hasattr(value, '_repr_html_'):
                value = value._repr_html_()
            else:
                value = _html_value(repr(value))
            msg = f'{symbol}は、{typename}。値は{value}'
            msgs.append(msg)
