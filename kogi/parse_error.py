import json
import linecache
import re
import sys
import re
import traceback

# from .render_html import render

from .parse_code import parse_find_name, parse_find_app, parse_find_index, parse_find_infix

DEFINED_ERRORS = []


def KOGI_ERR(**kw):
    global DEFINED_ERRORS
    defined = dict(**kw)
    if isinstance(defined['pattern'], str):
        defined['pattern'] = re.compile(defined['pattern'])
    if 'keys' in defined:
        defined['keys'] = tuple(defined['keys'].split(
            ',')) if ',' in defined['keys'] else (defined['keys'],)
    DEFINED_ERRORS.append(defined)

def DEBUG_ERR(**kw):
    global DEFINED_ERRORS
    defined = dict(**kw)
    if isinstance(defined['pattern'], str):
        defined['pattern'] = re.compile(defined['pattern'])
    if 'keys' in defined:
        defined['keys'] = tuple(defined['keys'].split(
            ',')) if ',' in defined['keys'] else (defined['keys'],)
    DEFINED_ERRORS = [defined] + DEFINED_ERRORS


# KOGI 定義

LANG_NAME = {
    'true': 'True',
    'false': 'False',
    'null': 'None',
    'NULL': 'None',
}

MODULE_ALIAS = {
    'math': 'math',
    'pd': 'pandas',
    'np': 'numpy',
}

MODULE_NAME = {
    'sin': 'math',
    'cos': 'math',
}

def check_name(slots, line):
    name = slots['matched']['name']
    slots['line'] = line
    if name in LANG_NAME:
        pyname = LANG_NAME[name]
        slots['translated'] = f'{name}は、Pythonでは{pyname}と書きます'
        slots['reason'] = f'別の言語の記法を使っている可能性が高いです'
        slots['hint'] = f'Pythonに早く慣れましょう'
        slots['solution'] = f'{name}を{pyname}に置き換えてください'
        return
    if name in MODULE_ALIAS:
        slots['reason'] = 'モジュールがインポートされていない'
        module_name = MODULE_ALIAS[name]
        slots['hint'] = f'モジュール名はたぶん {module_name}'
        if module_name == name:
            slots['solution'] = f'import {module_name}'
        else:
            slots['solution'] = f'import {module_name} as {name}'
        return
    ss = parse_find_name(line, name)
    id = 'モジュール'
    if len(ss) == 1:
        id = '変数もしくは定数' if ss[0]['ctype'] == 'var' else '関数'
    if name in MODULE_NAME:
        slots['reason'] = f'{id}がインポートされていない'
        module_name = MODULE_NAME[name]
        slots['hint'] = f'モジュール名はたぶん {module_name}'
        slots['solution'] = f'from {module_name} import {name}'
        return
    if id.startswith('変数'):
        slots['reason'] = f'{name}の単なる打ち間違い\nもしくは値を一度も代入していない'
        slots['hint'] = f'{name}の値は何ですか？考えてみよう'
        slots['solution'] = f'{name} = ... のように定義する'
    elif id.startswith('関数'):
        slots['reason'] = f'{name}の単なる打ち間違い\nもしくは関数やクラスを定義していない'
        slots['hint'] = f'実行忘れのセルがないか、確認してみよう'
    else:
        slots['hint'] = f'{name}の種類（変数、関数名、クラス名、モジュール名）を確認しましょう',


def test_NameError():
    print(undefined)


def test_NameError2():
    pd.read_csv('')


def test_NULL():
    print(null)


KOGI_ERR(
    pattern='name \'(.*?)\' is not defined',
    keys='name',
    translated='名前エラーです。\n{name}という名前を使いましたが、未定義です。\nつまり使える状態ではありません',
    check=check_name,
    reason='{name}の単なる打ち間違いかも',
    hint='{name}の種類（変数、関数名、モジュール名）を確認しましょう',
    solution='{name}の種類によって解決法は異なります',
    test=(test_NameError, test_NameError2, test_NULL),
)


def check_recv(slots, line):
    name = slots['matched']['name']
    type = slots['matched']['type']
    slots['line'] = line
    ss = parse_find_name(line, name, defined_key='recv')
    if len(ss) == 1:
        recv = ss[0]['recv']
        id = 'メソッド' if ss[0]['ctype'] == 'method' else 'プロパティ'
        slots['translated'] = f'型エラー: {recv}は{type}型です。{name}のような{id}はありません'
        slots['reason'] = f'{name}の打ち間違い、もしくは{recv}の{type}型が想定外'
        slots['hint'] = f'{recv}にが想定通りの型となるように修正してください'


def test_NoAttribute():
    d = {'a': 1}
    print(d.a)


def test_NoMethod():
    d = {'a': 1}
    print(d.a())


KOGI_ERR(
    pattern='\'(.*?)\' object has no attribute \'(.*?)\'',
    keys='type,name',
    translated='型エラー: レシーバは{type}型です。{name}のようなメソッドやプロパティはありません.',
    reason='{name}の打ち間違い、もしくはレシーバの型{type}が想定外',
    hint='レシーバが想定通りの型となるように修正してください',
    check=check_recv,
    test=(test_NoAttribute, test_NoMethod),
)


def test_ModuleNoAttribute():
    import math as m
    m.sins(1)


KOGI_ERR(
    pattern='module \'(.*?)\' has no attribute \'(.*?)\'',
    keys='module,name',
    translated='{module}モジュールには、{name}のような関数やプロパティはありません',
    reason='{name}の打ち間違いか、もしくは{module}を別のモジュールと勘違いしている',
    hint='dir({module})で利用できる名前を調べてみよう.',
    test=test_ModuleNoAttribute,
)


def test_ImportError():
    from math import sins


KOGI_ERR(
    pattern='ImportError: cannot import name \'(.*?)\' from \'(.*?)\'',
    keys='name,module',
    translated='{module}モジュールには、{name}のような関数やプロパティはありません',
    reason='{name}の打ち間違いか、もしくは{module}を別のモジュールと勘違いしている',
    hint='dir({module})で利用できる名前を調べてみよう.',
    test=test_ImportError,
)


def test_UnsupportedOperand():
    print(1+'2')


KOGI_ERR(
    pattern='unsupported operand type\(s\) for (.*?): \'(.*?)\' and \'(.*?)\'',
    keys='name,type,type2',
    translated='{type}と{type2}の間で計算しようとしたけど、そこでは演算子{name}は使えません.',
    solution='{type}か{type2}のどちらかの型に変換するといいかも',
    # inspect=inspect_infix,
    error_ext='{left}と{right}の間で計算しようとしたけど、型がそれぞれ{type}と{type2}で異なり、演算子{name}は使えません.',
    test=test_UnsupportedOperand,
)

KOGI_ERR(
    pattern='\'(.*?)\' not supported between instances of \'(.*?)\' and \'(.*?)\'',
    keys='name,type,type2',
    translated='{type}と{type2}の間で計算しようとしたけど、そこでは演算子{name}は使えません.',
    solution='{type}か{type2}のどちらかの型に変換するといいかも',
    # inspect=inspect_infix,
    error_ext='{left}と{right}の間で計算しようとしたけど、型がそれぞれ{type}と{type2}で異なり、演算子{name}は使えません.',
)


def check_callable(slots, lines):
    import builtins
    type = slots['matched']['type']
    ss = parse_find_app(lines)
    #print(ss)
    if len(ss) == 1 and 'cname' in ss[0]:
        name = ss[0]['cname']
        slots['translated'] = f'{name}の値は{type}型の値が代入されています。\n関数ではありません'
        slots['reason'] = f'{name}を変数名として代入してしまうと、関数として使えなくなります'
        slots['hint'] = f'{name}を何とかして関数に戻します'
        if name in dir(builtins):
            slots['solution'] = f'`from buitins import {name}`を試して'

def test_NotCallable():
    a = 1
    a()


KOGI_ERR(
    pattern='\'(.*?)\' object is not callable',
    keys='type',
    translated='{type}は、関数ではありません. ',
    hint='関数名を変数名として使ってしまうと発生します.',
    solution='環境を初期化してみてください',
    check=check_callable,
    test=test_NotCallable,
)


def test_NotIterable():
    list(1)


KOGI_ERR(
    pattern='\'(.*?)\' object is not iterable',
    keys='type',
    translated='{type}は、イテラブルではありません. つまり、列に変換できませんし、for文などで繰り返し処理もできません.',
    test=test_NotIterable,
)


def test_NotSubscriptable():
    a = 1
    a[0]


KOGI_ERR(
    pattern='\'(.*?)\' object is not subscriptable',
    keys='type',
    translated='{type}は、データ列でもマッピングでもありません.',
    reason='たぶん、x[y]のように操作したけど、xは[]で値を取れません。',
    test=test_NotSubscriptable,
)


def test_MustBeNoneOr():
    print(end=1)


KOGI_ERR(
    pattern='(\\w+?) must be None or a (\\w+?), not (\\w+)',
    keys='name,type,type2',
    translated='{name}は、Noneか{type}の値です. {type2}の値は使えません.',
    test=test_MustBeNoneOr,
)

#render_value() missing 1 required positional argument: 'value'
#TypeError: render_value() missing 2 required positional arguments: 'typename' and 'value'

KOGI_ERR(
    pattern='(\\S+?)\\(\\) missing (\\d+) required positional arguments?: (.*)$',
    keys='name,num,arguments',
    translated='型エラーです\n{name}には、{num}個の引数が足りません',
    reason='足りない引数は、{arguments}です。',
    solution='{name}の定義をよくみてください',
    #check=check_arguments,
)

def test_InvalidKeyword():
    print(color='red')


KOGI_ERR(
    pattern='\'(.*?)\' is an invalid keyword argument for (.*?)\\(\\)',
    keys='name,funcname',
    translated='{name}は、{funcname}の引数として使えるキーワードではありません.',
    solution='{funcname}のリファレンスを読んで確認してください.',
    test=test_InvalidKeyword,
)

KOGI_ERR(
    pattern='(\\S+?)\\(\\) got an unexpected keyword argument \'(.*?)\'',
    keys='funcname,name',
    translated='{name}は、{funcname}の引数として使えるキーワードではありません.',
    solution='{funcname}のリファレンスを読んで確認してください.',
)


KOGI_ERR(
    pattern='invalid (syntax)',
    keys='dummy',
    translated='構文エラーです',
    reason='Pythonは構文規則通りに書かなければなりません',
    hint='エラーの発生した前の行に問題があるかも',
)

KOGI_ERR(
    pattern='expected (an) indented block',
    keys='dummy',
    translated='構文エラー: インデントが足りません',
    reason='空白とタブが混ざっているかも',
    hint='エラーの発生した前の行に問題があるかも',
)

KOGI_ERR(
    pattern='unexpected (indent)',
    keys='dummy',
    translated='構文エラー: インデントが余分です',
    reason='空白とタブが混ざっているかも',
    hint='エラーの発生した前の行に問題があるかも',
)

KOGI_ERR(
    pattern='unindent does (not) match any outer indentation level',
    keys='dummy',
    translated='構文エラー: インデントの深さが変で、どのブロックに属すのかわかりません',
    reason='空白とタブが混ざっているかも',
    hint='エラーの発生した前の行に問題があるかも',
    solution='インデントの深さを揃えます',
)

KOGI_ERR(
    pattern='invalid (character) in identifier',
    keys='dummy',
    translated='構文エラー: 使用できない文字が使われています',
    reason='全角文字が混ざっている可能性が高いです',
    hint='先生やTAさんに質問する案件ではありません.',
    solution='落ち着いて打ち直そう',
)

KOGI_ERR(
    pattern='unexpected (EOF) while parsing',
    keys='dummy',
    translated='構文エラー: コードが途中までしか書かれていません. ',
    reason='たぶん、括弧やクオートを閉じ忘れている可能性が高いです.',
    hint='友達にチェックしてもらうとエラーが見つかるかも',
    solution='エラーの発生した行の前後を含めて、構文エラーを探して！',
)


def test_InvalidLiteral():
    int('a')


KOGI_ERR(
    pattern='invalid literal for int\(\) with base (.*?): (\'.*?\')',
    keys='base,value',
    translated='文字列{value}は、整数に変換できる文字列ではありません',
    test=test_InvalidLiteral,
)


def test_NotConvert():
    float('a')


KOGI_ERR(
    pattern='could not convert (\w+?) to (\w+?): \'(.*?)\'',
    keys='type,type2,value',
    translated='{type}の{value}は、{type2}に変換することはできません.',
    test=test_NotConvert,
)


def test_OutOfRange():
    s = "ABC"
    s[3]


KOGI_ERR(
    pattern='(\\w+) index out of range',
    keys='type',
    translated='インデックスが{type}の大きさを超えています. ',
    # nspect=inspect_index,
    error_ext='インデックス{index}が{callee}の大きさを超えています. ',
    solution_ext='インデックス{index}がlen({callee})未満に収まるように条件を加えてください. ',
    test=test_OutOfRange,
)


def test_KeyError():
    s = {}
    s["A"]


KOGI_ERR(
    pattern='KeyError: (.+?)$',
    keys='key',
    translated='キー{key}が見つかりません',
    # inspect=inspect_index,
    error_ext='{callee}にはキー{key}がありません. ',
    reason_ext='{index}が未定義なキー{key}として与えられています. ',
    solution_ext='{callee}のキーを確認しましょう. ',
    test=test_KeyError,
)


def test_MustBeInteger():
    s = "ABC"
    s['3']


KOGI_ERR(
    pattern='(\\w+) indices must be integers',
    keys='type',
    translated='{type}のインデックスは、整数でなければなりません.',
    # inspect=inspect_index,
    error_ext='{callee}のインデックスは、整数でなければなりません. ',
    reason_ext='{index}が整数でありません. ',
    solution_ext='{index}を整数に変換してみては？ ',
    test=test_MustBeInteger,
)


def test_DividedByZero():
    print(1/0)


KOGI_ERR(
    pattern='division by (zero)',
    keys='dummy',
    translated='ゼロで徐算しました. ',
    reason='ゼロで割ることはできません. ',
    hint='分母の値を確認してみましょう.',
    test=test_DividedByZero
)


def test_FileNotFoundError():
    open('file')


KOGI_ERR(
    pattern='FileNotFoundError: \\[Errno (\\d+)\\] No such file or directory: (\'.*\')',
    keys='errno,file',
    translated='{file}が見つかりません. ',
    reason='ファイル名やファイルパスが間違っている. ',
    hint='{file}が存在するか確認しよう.',
    test=test_FileNotFoundError,
)

# UsageError: Cell magic `%%kogi2` not found.

KOGI_ERR(
    pattern='UsageError: Cell magic `(.*)` not found',
    keys='name',
    translated='セルマジック{name}は、まだ使えません. ',
    reason='セルマチックをインポートし忘れています。',
    hint='何をインポートすべきか、{name}をググって探しましょう.',
)

# UsageError: %%kogi is a cell magic, but the cell body is empty.

KOGI_ERR(
    pattern='UsageError: (\\S.) is a cell magic, but the cell body is empty',
    keys='name',
    translated='{name}はセルマジックなので、本体が必要です',
    reason='セルマジックに続くべき、コードが空です',
    solution='セルの本文を書きましょう',
)


# ValueError: too many values to unpack (expected 2)

KOGI_ERR(
    pattern='ValueError: too many values to unpack \\(expected (\\d.)\\)',
    keys='num',
    translated='値エラー: {num}個の値を変数に展開しようとしたが、個数が不一致です。',
    reason='リストやタプルなどの値の数が、想定通りではない',
    hint='入力データも確認してみてください',
)


# error


def _format(ss, vocab):
    if isinstance(ss, str):
        return ss.format(**vocab)
    return [s.format(**vocab) for s in ss]


def _copy_and_format(defined, key, slots):
    if key in defined:
        slots[key] = _format(defined[key], slots['matched'])


def parse_error_message(code, emsg, lines):
    if emsg.startswith('Kogi'):
        _, _, data = emsg.partition(':')
        return json.loads(data)
    for defined in DEFINED_ERRORS:
        matched_result = defined['pattern'].search(emsg)
        if matched_result:
            matched = {}
            slots = dict(emsg=emsg, keys=defined['keys'], matched=matched)
            try:
                for i, key in enumerate(defined['keys']):
                    matched[key] = matched_result.group(i+1)
            finally:
                _copy_and_format(defined, 'translated', slots)
                _copy_and_format(defined, 'reason', slots)
                _copy_and_format(defined, 'hint', slots)
                _copy_and_format(defined, 'solution', slots)
            if 'check' in defined:
                try:
                    defined['check'](slots, lines)
                except:
                    traceback.print_exc()
            slots['code'] = code
            return slots
    return {'code': code, 'emsg': emsg}


def exception_stack(etype, evalue, tb):
    stacks = []
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        if 'lib' not in filename:
            name = tb.tb_frame.f_code.co_name
            lineno = tb.tb_lineno
            line = linecache.getline(filename, lineno, tb.tb_frame.f_globals)
            local_vars = tb.tb_frame.f_locals
            stacks.append(dict(filename=filename,
                               etype=f'{etype.__name__}',
                               emsg=f'{etype.__name__}: {evalue}',
                               name=name, lineno=lineno,
                               line=line, vars=local_vars))
        tb = tb.tb_next
    return list(stacks[::-1])


def parse_exception(code=None, print=print):
    etype, evalue, tb = sys.exc_info()
    emsg = f'{etype.__name__}: {evalue}'
    stacks = exception_stack(etype, evalue, tb)
    lines = [stack['line'].strip() for stack in stacks]
    return parse_error_message(code, emsg, lines)


def test_exception_hook():
    slots = parse_exception()
    print(slots)


if __name__ == '__main__':
    def test_DEFINED_ERRORS():
        for defined in DEFINED_ERRORS:
            fs = defined.get('test', ())
            if not isinstance(fs, tuple):
                fs = (fs,)
            for f in fs:
                try:
                    f()
                except:
                    test_exception_hook()

    test_DEFINED_ERRORS()
