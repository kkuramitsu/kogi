import pegtree as pg
import pandas as pd
from .logger import kogi_print
from .utils import zen2han


TYPE_PREFIX = {
    'type': 'クラス',
    'bool': 'ブール値',
    'int': '',
    'float': '',
    'dict': '辞書',
    'list': 'リスト',
    'tuple': 'タプル',
    'function': '関数',
    'set': 'セット',
    'deque': 'デック',
    'Counter': 'カウンタ',
    'ndarray': '配列',
    'DataFrame': 'データフレーム',
    'Series': 'データ列',
    'Symbol': 'シンボル',
    'AssocOp': '式',
}

FILEEXT = {
    'txt': 'テキストファイル',
    'csv': 'CSVファイル',
    'tsv': 'TSVファイル',
}


COLUMN_NAMES = set()


def update_columns(columns):
    COLUMN_NAMES.update(columns)


def detect_string_prefix(name, s):
    if s in COLUMN_NAMES:
        return 'カラム'
    _, sep, ext = s.rpartition('.')
    if sep == '.' and ext in FILEEXT:
        return FILEEXT[ext]
    if '{' in s and '}' in s:
        return '書式'
    return '文字列'


def detect_prefix(name, v):
    if isinstance(v, str):
        return detect_string_prefix(name, v)
    if isinstance(v, pd.DataFrame):
        update_columns(list(v.columns))
    typename = type(v).__name__
    if typename in TYPE_PREFIX:
        return TYPE_PREFIX[typename]
    supername = (type(v).__base__).__name__
    if supername in TYPE_PREFIX:
        return TYPE_PREFIX[supername]
    return ''  # '{typename}'

# code, prefix, key, index = prefix_index_code(str(fix(t)), index)


def prefix_code(code, index, always_policy=False):
    try:
        v = eval(code)
    except:
        if always_policy:
            return code, '', f'<e{index}>', index+1
        return code, '', '', index
    return code, detect_prefix(code, v), f'<e{index}>', index+1


PEG = '''
Start = {
    (Code _ / Chunk)*
    #Statement
}

Chunk = {
    . (!Code .)* #Chunk
}

Code = '`' { (!'`' .)+ #Code } '`' / { '<' (!'>' .)+ '>' #Special } / Expression

Expression =
  Suffix {^ OP Suffix #Binary }*

OP =
  / "==" / "!=" / "<=" / ">=" / "<>"
  / "**" / "//" / ">>" / "<<<" / ">>"
  / "+" / "-" / "*" / "/" / "%" / "="

Suffix = Primary _Postfix*

_Postfix =
  / {^ "(" Expression? ("," Expression )* ")" #App}
  / {^ "[" Expression? (([:,] _) Expression )* "]" #Index}

Primary =
  / Group
  / String
  / Name
  / Number

Group = 
  / "(" Expression ")"
  / { "[" Expression? ("," Expression)* ","? "]"  #List }
  / { "(" Expression? ("," Expression)* ","? ")"  #Tuple }

Name = 
  { [A-Za-z_] [A-Za-z_.0-9]* #Name } _

Number = 
  / { [0-9]+ ('.' [0-9]+)? #Number } _
  / { '.' [0-9]+ #Number } _

String =
  / { 'f'? '"'  (!'"' .)* '"' #String } _
  / { 'f'? "'" (!"'" .)*  "'" #String } _
'''

peg = pg.grammar(PEG)
parser = pg.generate(peg)


def _fix(tree):
    a = [tree.epos_]
    for t in tree:
        a.append(_fix(t).epos_)
    for key in tree.keys():
        a.append(_fix(tree.get(key)).epos_)
    tree.epos_ = max(a)
    return tree


def _replace_expression(s: str, always_policy=False):
    tree = parser(s)
    ss = []
    vars = {}
    index = 0
    # print(repr(tree))
    for t in tree:
        tag = t.getTag()
        if tag == 'Chunk' or tag == 'Special':
            ss.append(str(t))
        else:
            code = str(_fix(t))
            code, prefix, key, index = prefix_code(
                code, index, always_policy=always_policy)
            if key == '':
                ss.append(str(t))
            else:
                vars[key] = code
                ss.append(f'{prefix}{key}')
    return ''.join(ss), vars


def _replace_special(s: str, vars: dict) -> str:
    if isinstance(s, (list, tuple)):
        return tuple(_replace_special(x, vars) for x in s)
    for key in vars:
        s = s.replace(key, vars[key])
    return s


def _translate(s: str) -> str:
    return f'trans: {s}'


def compose(translate=_translate):
    def replace_around(s, always_policy=False, print=kogi_print):
        s = zen2han(s)
        if s.startswith('trans'):
            s, vars = _replace_expression(s, always_policy=always_policy)
            print('[BEFORE]', s)
            s = translate(s)
            print('[AFTER]', s)
            return _replace_special(s, vars)
        else:
            return translate(s)
    return replace_around


if __name__ == '__main__':
    tr = compose()
    tr('「a」をみる', always_policy=True, print=print)
