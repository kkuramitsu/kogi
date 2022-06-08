import logging
from .logger import kogi_print, log
import sys
from functools import wraps

from kogi.liberr import kogi_catch
from kogi.dialog import start_dialog
from kogi.problem import run_judge


try:
    InteractiveShell = get_ipython().__class__
except NameError:
    from IPython.core.interactiveshell import InteractiveShell


RUN_CELL = InteractiveShell.run_cell
SHOW_TRACEBACK = InteractiveShell.showtraceback
SHOW_SYNTAXERROR = InteractiveShell.showsyntaxerror

# newone


def change_run_cell(func):
    @wraps(func)
    def run_cell(*args, **kwargs):
        if len(args) > 1:
            ipyshell = args[0]
            raw_cell = args[1]
            if 'https://atcoder.jp/contests/' in raw_cell:
                #print('running cell ...')
                run_judge(raw_cell)
                args = list(args)
                args[1] = 'pass\n'
        value = func(*args, **kwargs)
        return value
    return run_cell


def change_showtraceback(func):
    @wraps(func)
    def showtraceback(*args, **kwargs):
        etype, evalue, tb = sys.exc_info()
        if etype is None:
            return func(*args, **kwargs)
        emsg = f"{etype.__name__}: {evalue}"
        if not emsg.startswith('KogiError'):
            value = func(*args, **kwargs)
        else:
            value = None
        ipyshell = args[0]
        if hasattr(ipyshell, 'run_cell_raw_cell'):
            raw_cell = ipyshell.run_cell_raw_cell
        else:
            raw_cell = None
        kogi_catch((etype, evalue, tb), code=raw_cell,
                   logging_json=log, dialog=start_dialog)
        return value

    return showtraceback


def enable_kogi_hook():
    # global KOGI_FN
    # KOGI_FN = kogi_fn
    InteractiveShell.run_cell = change_run_cell(RUN_CELL)
    InteractiveShell.showtraceback = change_showtraceback(SHOW_TRACEBACK)
    InteractiveShell.showsyntaxerror = change_showtraceback(SHOW_SYNTAXERROR)


def disable_kogi_hook():
    InteractiveShell.run_cell = RUN_CELL
    InteractiveShell.showtraceback = SHOW_TRACEBACK
    InteractiveShell.showsyntaxerror = SHOW_SYNTAXERROR
