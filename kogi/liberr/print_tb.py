import sys
import linecache


def bold(s):
    return f'\033[01m{s}\033[0m'


def glay(s):
    return f'\033[07m{s}\033[0m'


def red(s):
    return f'\033[31m{s}\033[0m'


def green(s):
    return f'\033[32m{s}\033[0m'


def yellow(s):
    return f'\033[33m{s}\033[0m'


def blue(s):
    return f'\033[34m{s}\033[0m'


def cyan(s):
    return f'\033[36m{s}\033[0m'


dots = green('...')

REPR_VALUE = {

}


def kogi_register_repr(typename, repr_func):
    REPR_VALUE[typename] = repr_func


def repr_value(value):
    typename = type(value).__name__
    if typename in REPR_VALUE:
        return REPR_VALUE[typename](value)
    if hasattr(value, '__name__'):
        return cyan(f'({typename})')+value.__name__
    if isinstance(value, list) and len(value) > 1:
        return f'[{value[0]}, {dots}]'
    if isinstance(value, str):
        return red(repr(value))
    return repr(value)


def repr_vars(vars):
    ss = []
    for key, value in vars.items():
        if key.startswith('_'):
            continue
        ss.append(f'{bold(key)}={repr_value(value)}')
    return ' '.join(ss)


def getline(filename, lines, n):
    if filename == '<string>':
        if 0 <= n-1 < len(lines):
            return lines[n-1]
        return ''
    return linecache.getline(filename, n).rstrip()


def arrow(lineno, here=False):
    s = str(lineno)
    if here:
        arrow = '-' * max(5-len(s), 0) + '> '
    else:
        arrow = ' ' * max(5-len(s), 0) + '  '
    return red(arrow) + green(f'{s}')


def filter_globals(vars, code):
    if 'get_ipython' in vars:
        newvars = {}
        for key, value in vars.items():
            if key in code:
                newvars[key] = value
        return newvars
    return vars


def print_func(filename, funcname, local_vars):
    print(f'"{glay(filename)}" {bold(funcname)} {repr_vars(local_vars)}')


def print_linecode(filename, lines, lineno):
    if lineno-2 > 0:
        print(arrow(lineno-2), getline(filename, lines, lineno-2))
    if lineno-1 > 0:
        print(arrow(lineno-1), getline(filename, lines, lineno-1))
    print(arrow(lineno, here=True), getline(filename, lines, lineno))
    print(arrow(lineno+1), getline(filename, lines, lineno+1))
    print(arrow(lineno+2), getline(filename, lines, lineno+2))


def kogi_print_exc(code='', exc_info=None):
    if exc_info is None:
        etype, evalue, tb = sys.exc_info()
    else:
        etype, evalue, tb = exc_info
    lines = code.splitlines()
    prev = None
    repeated = 0
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        funcname = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno
        local_vars = filter_globals(tb.tb_frame.f_locals, code)
        cur = (filename, funcname, lineno)
        if cur != prev:
            if repeated > 10:
                print(f'... repeated {red(str(repeated))} times ...')
            print_func(filename, funcname, local_vars)
            print_linecode(filename, lines, lineno)
            repeated = 0
        else:
            if repeated < 10:
                print_func(filename, funcname, local_vars)
            repeated += 1
        prev = cur
        tb = tb.tb_next

    print(f"{bold(red(etype.__name__))}: {bold(evalue)}")
