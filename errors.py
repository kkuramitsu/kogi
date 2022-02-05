import re
import traceback
import os
import sys
import re


def _deco(s, type='name', return_html=True):
    if return_html == True:
        if type.startswith('name'):
            return f'<span class="{type}">{s}</span>'
    return s


DEFINED_ERRORS = []


def CORGI_ERR(d):
    global DEFINED_ERRORS
    DEFINED_ERRORS.append(d)


def _translate_error(errtype, errmsg, code=None, errlines=None, return_html=True):
    s = f'{errtype}: {errmsg}'
    results = {'errtype': errtype, 'error': s}
    for defined in DEFINED_ERRORS:
        if isinstance(defined['pattern'], str):
            defined['pattern'] = re.compile(defined['pattern'])
            defined['keys'] = tuple(defined['keys'].split(','))
        matched = defined['pattern'].search(s)
        if matched:
            for i, key in enumerate(defined['keys']):
                if key == '':
                    break
                results[key] = matched.group(i+1)
            if 'inspect' in defined:
                defined['inspect'](code, errlines, results)
            if 'error_ext' in defined:
                ext_messages = defined['error_ext']
                for ext in ext_messages.keys():
                    if ext in results:
                        results['translated'] = ext_messages[ext].format(
                            **results)
                        return results
            results['translated'] = defined['error'].format(**results)
            return results
    return results


LinePat = re.compile(r'line (\d+)')
#print(LinePat.match('aa line 18, in <module>'))


def _get_error_lines():
    ss = []
    formatted_lines = traceback.format_exc().splitlines()
    for i, line in enumerate(formatted_lines):
        #print(i, line)
        # if 'ipython-input' in line and ', in ' in line:
        if ', in ' in line:
            matched = LinePat.search(line)
            if matched:
                # ss.append((int(matched.group(1)), formatted_lines[i+1]))
                ss.append(formatted_lines[i+1])
    return ss[::-1]


def corgi_translate_error(code=None, verbose=False, return_html=False):
    exc_type, exc_value, _ = sys.exc_info()
    error_lines = _get_error_lines()
    results = _translate_error(
        f'{exc_type.__name__}', exc_value, code, error_lines, return_html=False)
    if verbose:
        print(results['error'])
        print(' =>', results.get('translated'), '')
    return results


def _find_index_callee(lines, index=None):
    if lines is None:
        return None
    if index is not None:
        pattern = f'((\\w|\\.)+?)\\[[\'\"]?{index}[\'\"]?\\]'
    else:
        pattern = f'((\\w|\\.)+?)\\['
    if isinstance(lines, str):
        lines = [lines]
    for line in lines:
        matched = re.search(pattern, line)
        if matched:
            return matched.group(1)
    return None


_find_index_callee("print(1+math.d['a'])", "a")


# CORGI 定義

def test_NameError():
    try:
        print(undefined)
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': 'name \'(.*?)\' is not defined',
    'keys': 'name',
    'error': '変数名{name}は、打ち間違いか、まだインポートされていないか、とにかく未定義です',
    'test': test_NameError,
})


def _inspect_method_callee(code, lines, slots):
    if lines is None:
        return

    suffix = slots.get('name', 'undefined')
    pattern = re.compile(f'((\\w|\\.)+?)\\.{suffix}\\s*(.?)')

    if isinstance(lines, str):
        lines = [lines]
    for line in lines:
        matched = pattern.search(line+' ')
        if matched:
            next_char = matched.group(3)
            if next_char.isascii() and next_char.isalnum():
                continue
            slots['callee'] = matched.group(1)
            if next_char == '(':
                slots['nametype'] = 'メソッド'
            else:
                slots['nametype'] = 'プロパティ'
            return


def test_NoAttribute():
    try:
        d = {'a': 1}
        print(d.a)
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': '\'(.*?)\' object has no attribute \'(.*?)\'',
    'keys': 'type,name',
    'error': '{type}には、{name}のようなメソッドやプロパティはありません.',
    'test': test_NoAttribute,
    'inspect': _inspect_method_callee,
    'error_ext': {
        'callee': '''{callee}は、{type}です. {name}のような{nametype}はありません.
{callee}の型は、{type}で正しいですか？
 - もし正しいなら、{name}の打ち間違いを確認してください.
 - もし正しくないなら、どこかで{name}に間違った値が代入されています. '''
    }
})


def test_ModuleNoAttribute():
    try:
        import math
        math.sins(1)
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': 'module \'(.*?)\' has no attribute \'(.*?)\'',
    'keys': 'name,name2',
    'error': '{name}モジュールには、{name2}のような関数やプロパティはありません',
    'test': test_ModuleNoAttribute,
})


def test_UnsupportedOperand():
    try:
        print(1+'2')
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': 'unsupported operand type\(s\) for (.*?): \'(.*?)\' and \'(.*?)\'',
    'keys': 'name,type,type2',
    'error': '{type}と{type2}の間で演算子{name}を計算しようとしたけど、そこでは使えません.',
    'test': test_UnsupportedOperand,
})

CORGI_ERR({
    'pattern': '\'(.*?)\' not supported between instances of \'(.*?)\' and \'(.*?)\'',
    'keys': 'name,type,type2',
    'error': '{type}と{type2}の間で演算子{name}を計算しようとしたけど、そこでは使えません.'
})


def test_NotCallable():
    try:
        a = 1
        a()
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': '\'(.*?)\' object is not callable',
    'keys': 'type',
    'error': '{type}は、関数ではありません. たぶん、関数名に{type}の値を間違って代入してしまったため関数適用できません.',
    'test': test_NotCallable,
})


def test_NotIterable():
    try:
        list(1)
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': '\'(.*?)\' object is not iterable',
    'keys': 'type',
    'error': '{type}は、イテラブルではありません. つまり、リストに変換できませんし、for文などで繰り返し処理もできません.',
    'test': test_NotIterable,
})


def test_NotSubscriptable():
    try:
        a = 1
        a[0]
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': '\'(.*?)\' object is not subscriptable',
    'keys': 'type',
    'error': '{type}は、データ列でもマッピングでもありません.',
    'test': test_NotSubscriptable,
})


def test_MustBeNoneOr():
    try:
        print(end=1)
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': '(\\w+?) must be None or a (\\w+?), not (\\w+)',
    'keys': 'name,type,type2',
    'error': '{name}は、Noneか{type}の値です. {type2}の値は使えません.',
    'test': test_MustBeNoneOr,
})


def test_InvalidKeyword():
    try:
        print(color='red')
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': '\'(.*?)\' is an invalid keyword argument for (.*?)\\(\\)',
    'keys': 'name,name2',
    'error': '{name}は、関数もしくはメソッド{name2}で使えるキーワード引数ではありません.',
    'test': test_InvalidKeyword,
})

CORGI_ERR({
    'pattern': '(.*?)\\(\\) got an unexpected keyword argument \'(.*?)\'',
    'keys': 'name,name2',
    'error': '{name2}は、関数もしくはメソッド{name}で使えるキーワード引数ではありません.'
})


CORGI_ERR({
    'pattern': 'expected an indented block',
    'keys': '',
    'error': 'ここでインデントされるはずです'
})

CORGI_ERR({
    'pattern': 'invalid character in identifier',
    'keys': '',
    'error': '半角文字を使うべきところで、全角文字が混ざって使われています'
})

CORGI_ERR({
    'pattern': 'unexpected EOF while parsing',
    'keys': '',
    'error': 'コードが途中までしか書かれていません. たぶん、括弧やクオートの閉じ忘れの可能性が高いです.'
})


def test_InvalidLiteral():
    try:
        int('a')
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': 'invalid literal for int\(\) with base (.*?): (\'.*?\')',
    'keys': 'base,value',
    'error': '文字列{value}は、整数に変換できる文字列ではありません',
    'test': test_InvalidLiteral,
})


def test_NotConvert():
    try:
        float('a')
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': 'could not convert (\w+?) to (\w+?): \'(.*?)\'',
    'keys': 'type,type2,value',
    'error': '{type}の{value}は、{type2}に変換することはできません.',
    'test': test_NotConvert,
})


def test_OutOfRange():
    try:
        s = "ABC"
        s[3]
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': '(\\w+) index out of range',
    'keys': 'type',
    'error': 'インデックスが{type}の大きさを超えています. ',
    'test': test_OutOfRange,
})


def test_MustBeInteger():
    try:
        s = "ABC"
        s['3']
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': '(\\w+) indices must be integers',
    'keys': 'type',
    'error': '{type}のインデックスは、整数でなければなりません.',
    'test': test_MustBeInteger,
})


def test_KeyError():
    try:
        s = "ABC"
        s[3]
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': 'KeyError: (.*?)',
    'keys': 'key',
    'error': 'キー{key}が見つかりません',
    'test': test_KeyError,
})


def test_DividedByZero():
    try:
        print(1/0)
    except:
        corgi_translate_error(verbose=True)


CORGI_ERR({
    'pattern': 'division by zero',
    'keys': '',
    'error': 'ゼロで割り算しました. 分母の値を確認してみましょう.',
    'test': test_DividedByZero
})


def test_DEFINED_ERRORS():
    for defined in DEFINED_ERRORS:
        if 'test' in defined:
            defined['test']()


if __name__ == '__main__':
    test_DEFINED_ERRORS()


# CODE_STYLE = '''
# 拡大するから落ち着いて、構文エラーを探してね
# <div style="white-space: pre; font-family: monospace; font-size: 16pt; ">$CODE
# </div>
# '''

# def _magnify_code(code, msgs, return_html=True):
#   if return_html and code is not None:
#     ss = []
#     for c in code:
#       if c == '\t':
#         ss.append(f'<span style="background: lightblue; color: white">→→</span>')
#       elif ord(c) > 126:
#         ss.append(f'<span style="background: pink; color: white">{c}</span>')
#       else:
#         ss.append(c)
#     msgs.append(CODE_STYLE.replace('$CODE', ''.join(ss)))
