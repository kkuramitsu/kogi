import re
import traceback
import sys
import re

from .render_html import render

from .error_inspect import inspect_callee, inspect_infix, inspect_funcname, inspect_index

DEFINED_ERRORS = []


def KOGI_ERR(d):
    global DEFINED_ERRORS
    DEFINED_ERRORS.append(d)


def KOGI_ERR2(**kw):
    global DEFINED_ERRORS
    DEFINED_ERRORS.append(dict(**kw))


def _format(ss, results):
    vocab = results
    if isinstance(ss, str):
        return ss.format(**vocab)
    return [s.format(**vocab) for s in ss]


def _formatting(defined, key, ext, results):
    key_ext = key+ext
    if key_ext in defined:
        results[key] = _format(defined[key_ext], results)
        return
    if ext == '' and key in defined:
        results[key] = _format(defined[key_ext], results)
        return


def _check_error(errtype, errmsg, code=None, errlines=None, render_html=True):
    s = f'{errtype}: {errmsg}'
    results = {'error_type': errtype, 'error': s}
    for defined in DEFINED_ERRORS:
        if isinstance(defined['pattern'], str):
            defined['pattern'] = re.compile(defined['pattern'])
            defined['keys'] = tuple(defined['keys'].split(','))
        matched = defined['pattern'].search(s)
        if matched:
            for i, key in enumerate(defined['keys']):
                if key == '':
                    break
                results[key] = render(matched.group(
                    i+1), key, render_html=render_html)
            _ext = ''
            if 'inspect' in defined:
                _ext = defined['inspect'](code, errlines, results)
            if 'error_type' in defined:
                results['error_type'] = defined['error_type']
            results['error_orig'] = results['error']
            _formatting(defined, 'error', _ext, results)
            _formatting(defined, 'reason', _ext, results)
            _formatting(defined, 'solution', _ext, results)
            _formatting(defined, 'hint', _ext, results)
            return results
    return results


LinePat = re.compile(r'line (\d+)')
# print(LinePat.match('aa line 18, in <module>'))


def _get_error_lines():
    ss = []
    formatted_lines = traceback.format_exc().splitlines()
    for i, line in enumerate(formatted_lines):
        # print(i, line)
        # if 'ipython-input' in line and ', in ' in line:
        if ', in ' in line:
            matched = LinePat.search(line)
            if matched:
                # ss.append((int(matched.group(1)), formatted_lines[i+1]))
                ss.append(formatted_lines[i+1])
    return ss[::-1]


def _show_verbose(results):
    if 'error_orig' in results:
        print(results['error_orig'])
        print(' =>', results.get('error'), '')
        if 'reason' in results:
            print(' reason: ', results.get('reason'), '')
        if 'solution' in results:
            print(' solution:', results.get('solution'), '')


def kogi_check_error(code=None, show=_show_verbose, render_html=False):
    exc_type, exc_value, _ = sys.exc_info()
    error_lines = _get_error_lines()
    results = _check_error(
        f'{exc_type.__name__}', exc_value, code, error_lines, render_html=render_html)
    show(results)
    return results


# kogi 定義

def test_NameError():
    try:
        print(undefined)
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='name \'(.*?)\' is not defined',
    keys='name',
    error='{name}という名前を使おうとしましたが、まだ一度も使われていません',
    reason=[
        '{name}の単なる打ち間違い',
        '{name}が変数なら、まだ一度も値を代入していない `{name} = ...`',
        '{name}が関数名やクラス名なら未定義、もしくは定義したセルを実行していない',
        '{name}がモジュールなら正しくインポートされていない `import {name}` ',
    ],
    solution='{name}の種類をちゃんと確認しましょう',
    hint='「{name}をインポートするには？」と聞いてみる',
    test=test_NameError,
)


def test_NoAttribute():
    try:
        d = {'a': 1}
        print(d.a)
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='\'(.*?)\' object has no attribute \'(.*?)\'',
    keys='type,name',
    error='{type}には、{name}のようなメソッドやプロパティはありません.',
    reason='{name}の打ち間違い、もしくは間違った値が使われている.',
    solution='間違った値が代入された箇所を探してください.',
    inspect=inspect_callee,
    error_ext='{callee}は、{type}です. {name}のような{pyname}はありません.',
    reason_ext='{name}{pyname}の打ち間違い、もしくは{callee}に間違った型の値が代入されている.',
    solution_ext='{callee}に間違った値を代入した箇所を探してください.',
    test=test_NoAttribute,
)


def test_ModuleNoAttribute():
    try:
        import math as m
        m.sins(1)
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='module \'(.*?)\' has no attribute \'(.*?)\'',
    keys='module,name',
    error='{module}モジュールには、{name}のような関数やプロパティはありません',
    reason='{name}の打ち間違いでは？',
    solution='dir({module})で利用できる名前を調べてみよう.',
    inspect=inspect_callee,
    error_ext='{module}モジュールには、{name}のような{pyname}はありません',
    test=test_ModuleNoAttribute,
)


def test_ImportError():
    try:
        from math import sins
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='ImportError: cannot import name \'(.*?)\' from \'(.*?)\'',
    keys='name,module',
    error='モジュール{module}には{name}が見つかりません. ',
    reason='{name}の打ち間違いか、モジュール{module}の勘違い．',
    solution='dir({module})で利用できる名前を調べてみよう.',
    test=test_ImportError,
)


def test_UnsupportedOperand():
    try:
        print(1+'2')
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='unsupported operand type\(s\) for (.*?): \'(.*?)\' and \'(.*?)\'',
    keys='name,type,type2',
    error='{type}と{type2}の間で計算しようとしたけど、そこでは演算子{name}は使えません.',
    solution='{type}か{type2}のどちらかの型に変換するといいかも',
    inspect=inspect_infix,
    error_ext='{left}と{right}の間で計算しようとしたけど、型がそれぞれ{type}と{type2}で異なり、演算子{name}は使えません.',
    test=test_UnsupportedOperand,
)

KOGI_ERR2(
    pattern='\'(.*?)\' not supported between instances of \'(.*?)\' and \'(.*?)\'',
    keys='name,type,type2',
    error='{type}と{type2}の間で計算しようとしたけど、そこでは演算子{name}は使えません.',
    solution='{type}か{type2}のどちらかの型に変換するといいかも',
    inspect=inspect_infix,
    error_ext='{left}と{right}の間で計算しようとしたけど、型がそれぞれ{type}と{type2}で異なり、演算子{name}は使えません.',
)


def test_NotCallable():
    try:
        a = 1
        a()
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='\'(.*?)\' object is not callable',
    keys='type',
    error='{type}は、関数ではありません. ',
    reason='変数名に{type}の値を間違って代入してしまうと発生することがあります.',
    solution='環境を初期化してみてください',
    inspect=inspect_funcname,
    error_ext='{name}は、{type}型であり、関数ではありません. ',
    reason_ext='{name}に{type}の値を代入してしまうと、発生します.',
    test=test_NotCallable,
)


def test_NotIterable():
    try:
        list(1)
    except:
        kogi_check_error()


KOGI_ERR({
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
        kogi_check_error()


KOGI_ERR({
    'pattern': '\'(.*?)\' object is not subscriptable',
    'keys': 'type',
    'error': '{type}は、データ列でもマッピングでもありません.',
    'reason': 'たぶん、x[y]のように操作したけど、xは[]で値を取れません。',
    'test': test_NotSubscriptable,
})


def test_MustBeNoneOr():
    try:
        print(end=1)
    except:
        kogi_check_error()


KOGI_ERR({
    'pattern': '(\\w+?) must be None or a (\\w+?), not (\\w+)',
    'keys': 'name,type,type2',
    'error': '{name}は、Noneか{type}の値です. {type2}の値は使えません.',
    'test': test_MustBeNoneOr,
})


def test_InvalidKeyword():
    try:
        print(color='red')
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='\'(.*?)\' is an invalid keyword argument for (.*?)\\(\\)',
    keys='name,funcname',
    error='{name}は、{funcname}の引数として使えるキーワードではありません.',
    solution='{funcname}のリファレンスを読んで確認してください.',
    test=test_InvalidKeyword,
)

KOGI_ERR2(
    pattern='(.*?)\\(\\) got an unexpected keyword argument \'(.*?)\'',
    keys='funcname,name',
    error='{name}は、{funcname}の引数として使えるキーワードではありません.',
    solution='{funcname}のリファレンスを読んで確認してください.',
)


KOGI_ERR2(
    pattern='invalid syntax',
    keys='',
    error='構文エラーです',
    reason='Pythonは構文規則通りに書かなければなりません',
)

KOGI_ERR2(
    pattern='expected an indented block',
    keys='',
    error='インデントが足りません',
)

KOGI_ERR2(
    pattern='unexpected indent',
    keys='',
    error='インデントが余分です',
)

KOGI_ERR2(
    pattern='unindent does not match any outer indentation level',
    keys='',
    error='インデントの深さが変で、どのブロックに属すのかわかりません',
    solution='インデントの深さを揃えます',
)

KOGI_ERR2(
    pattern='invalid character in identifier',
    keys='',
    error='半角文字を使うべきところで、全角文字が混ざって使われています',
    solution='日本語入力をオフにして、打ち直そう',
    hint='先生やTAさんに質問する案件ではありません.',
)

KOGI_ERR2(
    pattern='unexpected EOF while parsing',
    keys='',
    error='コードが途中までしか書かれていません. ',
    reason='たぶん、括弧やクオートの閉じ忘れの可能性が高いです.',
    solution='エラーの発生した行の前後を含めて、構文エラーを探して！',
    hint='友達にチェックしてもらうとエラーが見つかるかも',
)


def test_InvalidLiteral():
    try:
        int('a')
    except:
        kogi_check_error()


KOGI_ERR({
    'pattern': 'invalid literal for int\(\) with base (.*?): (\'.*?\')',
    'keys': 'base,value',
    'error': '文字列{value}は、整数に変換できる文字列ではありません',
    'test': test_InvalidLiteral,
})


def test_NotConvert():
    try:
        float('a')
    except:
        kogi_check_error()


KOGI_ERR({
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
        kogi_check_error()


KOGI_ERR2(
    pattern='(\\w+) index out of range',
    keys='type',
    error='インデックスが{type}の大きさを超えています. ',
    inspect=inspect_index,
    error_ext='インデックス{index}が{callee}の大きさを超えています. ',
    solution_ext='インデックス{index}がlen({callee})未満に収まるように条件を加えてください. ',
    test=test_OutOfRange,
)


def test_KeyError():
    try:
        s = {}
        s["A"]
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='KeyError: (.+?)$',
    keys='key',
    error='キー{key}が見つかりません',
    inspect=inspect_index,
    error_ext='{callee}にはキー{key}がありません. ',
    reason_ext='{index}が未定義なキー{key}として与えられています. ',
    solution_ext='{callee}のキーを確認しましょう. ',
    test=test_KeyError,
)


def test_MustBeInteger():
    try:
        s = "ABC"
        s['3']
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='(\\w+) indices must be integers',
    keys='type',
    error='{type}のインデックスは、整数でなければなりません.',
    inspect=inspect_index,
    error_ext='{callee}のインデックスは、整数でなければなりません. ',
    reason_ext='{index}が整数でありません. ',
    solution_ext='{index}を整数に変換してみては？ ',
    test=test_MustBeInteger,
)


def test_DividedByZero():
    try:
        print(1/0)
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='division by zero',
    keys='',
    error='ゼロで割り算しました. ',
    reason='ゼロで割ることはできません. ',
    solution='分母の値を確認してみましょう.',
    test=test_DividedByZero
)


def test_FileNotFoundError():
    try:
        open('file')
    except:
        kogi_check_error()


KOGI_ERR2(
    pattern='FileNotFoundError: \\[Errno (\\d+)\\] No such file or directory: (\'.*\')',
    keys='errno,file',
    error='{file}が見つかりません. ',
    reason='ファイル名やファイルパスが間違っている. ',
    solution='{file}が存在するか確認しよう.',
    test=test_FileNotFoundError,
)


def test_DEFINED_ERRORS():
    for defined in DEFINED_ERRORS:
        if 'test' in defined:
            defined['test']()


if __name__ == '__main__':
    test_DEFINED_ERRORS()
