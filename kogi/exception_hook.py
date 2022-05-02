from IPython.core.interactiveshell import InteractiveShell
from functools import wraps
import sys
#import traceback
import linecache
import json

from .exception_dialog import exception_dialog
from .logger import kogi_print, log

RUN_CELL = InteractiveShell.run_cell
SHOW_TRACEBACK = InteractiveShell.showtraceback
SHOW_SYNTAXERROR = InteractiveShell.showsyntaxerror


def stack_traceback(etype, emsg, tb):
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
                               emsg=emsg,
                               name=name, lineno=lineno, line=line,
                               vars=local_vars))
        tb = tb.tb_next
    return list(stacks[::-1])


class KogiError(Exception):
    def __init__(self, **kw):
        Exception.__init__(self, json.dumps(kw))


def dummy_kogi_fn(raw_cell, emsg, stacks):
    kogi_print(raw_cell)
    kogi_print(emsg)
    kogi_print(stacks)


KOGI_FN = exception_dialog


def exception_hook(raw_cell, emsg, stacks):
    traceback = []
    for stack in stacks:
        d = stack.copy()
        del d['vars']
        traceback.append(d)
    log(
        type='exception_hook',
        code=raw_cell, emsg=emsg,
        traceback=traceback
    )
    try:
        KOGI_FN(raw_cell, emsg, stacks)
    except Exception as e:
        kogi_print(e)


def change_run_cell(func):
    @wraps(func)
    def run_cell(*args, **kwargs):
        if len(args) > 1:
            ipyshell = args[0]
            raw_cell = args[1]
            ipyshell.run_cell_raw_cell = raw_cell
        value = func(*args, **kwargs)
        return value
    return run_cell


def change_showtraceback(func):
    @wraps(func)
    def showtraceback(*args, **kwargs):
        etype, evalue, tb = sys.exc_info()
        emsg = f"{etype.__name__}: {evalue}"
        if not emsg.startswith('KogiError'):
            value = func(*args, **kwargs)
        else:
            value = None
        ipyshell = args[0]
        raw_cell = ipyshell.run_cell_raw_cell
        stacks = stack_traceback(etype, emsg, tb)
        exception_hook(raw_cell, emsg, stacks)
        return value
    return showtraceback


def enable_kogi_hook(kogi_fn=exception_dialog):
    global KOGI_FN
    KOGI_FN = kogi_fn
    InteractiveShell.run_cell = change_run_cell(RUN_CELL)
    InteractiveShell.showtraceback = change_showtraceback(SHOW_TRACEBACK)
    InteractiveShell.showsyntaxerror = change_showtraceback(SHOW_SYNTAXERROR)


def disable_kogi_hook():
    InteractiveShell.run_cell = RUN_CELL
    InteractiveShell.showtraceback = SHOW_TRACEBACK
    InteractiveShell.showsyntaxerror = SHOW_SYNTAXERROR
