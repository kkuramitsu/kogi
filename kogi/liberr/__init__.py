import linecache
import sys
import os
import string

try:
    import pegtree as pg
except ModuleNotFoundError:
    os.system('pip3 install pegtree')
    import pegtree as pg


_PEG = '''

Start = { 
    (Param /  { (!Param .)* } )*
}

Param = LQuote / Quote / DoubleQuote / BackQuote 
    / Data / FuncName / CellName/ VarName 
    / ClassName / PathName / UName
    / Float / Int / Hex

LQuote = LQuote1 / LQuote2 / LQuote3
LQuote1 = {'\\'(' (!')\\'' . )+ ')\\'' #Quote}
LQuote2 = {'\\'<' (!'>\\'' . )+ '>\\'' #Quote}
LQuote3 = {'\\'[' ('\\\\' '\\'' / !']\\'' . )+ ']\\'' #Quote}
Quote = { '\\'' (!'\\'' .)* '\\'' #Quote }
BackQuote = { '`' (!'`' .)* '`' #Quote }
DoubleQuote = { '"' (![" ] .)* '"' #Quote }

Data = Set / Tuple
Set = { '{' ( Data / !'}' . )* '}' #Set }
Tuple = { '[' ( Data / !']' . )* ']' #Tuple }

FuncName = { NAME &'()' #FuncName }
CellName = { '%' '%'? NAME  #CellName }
VarName = { NAME ('\\'' NAME)? }  // can't
NAME = [A-Za-z_] [A-Za-z_0-9]*
ClassName = { '<' [A-Za-z] (!'>' .)* '>' #ClassName }
PathName = { '(/' (!')' .)+ ')' #Path }


Float = { [0-9]* '.' [0-9]+ #Number }
Int = { [0-9]+ ![A-Za-z] #Int }
Hex = { '0x' [0-9A-Fa-f]+ #Hex }

UName = { U (!END .)* #UName }
END = [ (),]

U = [ぁ-んァ-ヶ㐀-䶵一-龠々〇〻ー]

'''

_parser = pg.generate(pg.grammar(_PEG))
_IDX = string.ascii_uppercase


def extract_params_from_error(emsg):
    tree = _parser(emsg)
    ss = []
    params = []
    for t in tree:
        s = str(t)
        if t == '':
            ss.append(s)
            continue
        idx = _IDX[len(params) % 26]
        # if t == 'Quote':
        #     quote=s[0]
        #     idx = f'{quote}{idx}{quote}'
        ss.append(idx)
        params.append(s)
    return ''.join(ss), params


def _safe(s):
    ss = list(s)
    for i in range(len(ss)-1):
        if 'A' <= ss[i] <= 'Z':
            c = ss[i+1]
            if 'A' <= c <= 'z' or '0' <= c <= '9' or c == '_':
                pass
            else:
                ss[i] = f'_{ss[i]}_'
    return ''.join(ss)


def _unquote(s, fmt='{}'):
    if s[0] == s[-1] and s[0] == "'" or s[0] == '`':
        s2 = s[1:-1]
        for c in s2:
            if ord(c) > 127 or not c.isalnum() and c != '_':
                return s
        return fmt.format(s2)
    return fmt.format(s)


def abspath(file):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), file)


class ErrorModel(object):
    def __init__(self, file=None):
        self.eDict = {}
        if file is not None:
            self.load(file)

    def load(self, file='emsg_translated_ja.txt'):
        if not os.path.exists(file):
            file = abspath(file)
        with open(file) as f:
            index = 0
            lines = ['', '']
            for line in f.readlines():
                line = line.strip()
                if line == '':
                    index = 0
                    continue
                lines[index] = line
                index += 1
                if index == 2:
                    self.eDict[lines[0]] = lines[1]
                    index = 0
        #print('loaded', len(self.eDict))

    def find_new(self, series):
        ss = set()
        for emsg in series:  # df['emsg']
            emsg = emsg.strip()
            emsg, params = extract_params_from_error(emsg)
            # print(emsg)
            ss.add(emsg)
            #print('\t', params)
        for s in ss:
            if len(s) < 256:
                if s not in self.eDict:
                    print(s)
                print(s, file=f)
        #print(len(series), '=>', len(ss))

    def translate(self, emsg, unquote_format='{}'):
        t, params = extract_params_from_error(emsg)
        #print(t, params, t in self.eDict)
        if t in self.eDict:
            t = self.eDict[t]
            t = _safe(t)
            for X, val in zip(string.ascii_uppercase, params):
                t = t.replace(f'_{X}_', _unquote(val, fmt=unquote_format))
            return t
        return emsg


_defaultErrorModel = ErrorModel('emsg_translated_ja.txt')


def catch_exception(include_locals=False, include_translated=True):
    etype, evalue, tb = sys.exc_info()
    emsg = (f"{etype.__name__}: {evalue}").strip()

    stacks = []
    stack_vars = []
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        if 'lib' not in filename:
            name = tb.tb_frame.f_code.co_name
            lineno = tb.tb_lineno
            line = linecache.getline(filename, lineno, tb.tb_frame.f_globals)
            local_vars = tb.tb_frame.f_locals
            stacks.append(dict(filename=filename,
                               etype=f'{etype.__name__}', emsg=emsg,
                               name=name, lineno=lineno, line=line))
            stack_vars.append(local_vars)
        tb = tb.tb_next
    results = dict(etype=f'{etype.__name__}',
                   emsg=emsg, stacks=list(stacks[::-1]))
    if include_locals:
        results['locals'] = list(stack_vars[::-1])
    if include_translated:
        translated = _defaultErrorModel.translate(emsg)
        if translated != emsg:
            results['translated'] = translated
    return results
