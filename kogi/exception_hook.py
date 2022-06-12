import traceback
import sys
from functools import wraps

#from kogi.problem import run_judge
from .logger import kogi_print, log

# try:
#     from IPython import get_ipython
#     InteractiveShell = get_ipython().__class__
# except NameError:
from IPython.core.interactiveshell import InteractiveShell


RUN_CELL = InteractiveShell.run_cell
SHOW_TRACEBACK = InteractiveShell.showtraceback
SHOW_SYNTAXERROR = InteractiveShell.showsyntaxerror

# newone


def change_run_cell(func, run_judge):
    @wraps(func)
    def run_cell(*args, **kwargs):
        try:
            if len(args) > 1:
                ipyshell = args[0]
                raw_cell = args[1]
                if 'https://atcoder.jp/contests/' in raw_cell:
                    #print('running cell ...')
                    code = run_judge(raw_cell)
                    args = list(args)
                    args[1] = code
        except:
            traceback.print_exc()
        value = func(*args, **kwargs)
        return value
    return run_cell


def change_showtraceback(func, kogi_catch):
    @wraps(func)
    def showtraceback(*args, **kwargs):
        sys_exc = sys.exc_info()
        value = func(*args, **kwargs)
        try:
            # ipyshell = args[0]
            # if hasattr(ipyshell, 'run_cell_raw_cell'):
            #     raw_cell = ipyshell.run_cell_raw_cell
            # else:
            #     raw_cell = None
            kogi_catch(sys_exc, code=None)
        except:
            traceback.print_exc()
        return value

    return showtraceback


def enable_kogi_hook(run_judge, kogi_catch):
    InteractiveShell.run_cell = change_run_cell(RUN_CELL, run_judge)
    InteractiveShell.showtraceback = change_showtraceback(
        SHOW_TRACEBACK, kogi_catch)
    InteractiveShell.showsyntaxerror = change_showtraceback(
        SHOW_SYNTAXERROR, kogi_catch)


def disable_kogi_hook():
    InteractiveShell.run_cell = RUN_CELL
    InteractiveShell.showtraceback = SHOW_TRACEBACK
    InteractiveShell.showsyntaxerror = SHOW_SYNTAXERROR
