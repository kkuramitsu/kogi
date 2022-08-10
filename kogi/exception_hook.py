import traceback
from functools import wraps

from kogi.logger import sync_lazy_loggger

from .dialog import kogi_catch
from IPython.core.interactiveshell import InteractiveShell, ExecutionResult


RUN_CELL = InteractiveShell.run_cell
SHOW_TRACEBACK = InteractiveShell.showtraceback
SHOW_SYNTAXERROR = InteractiveShell.showsyntaxerror


DETECTOR = []
RUNNER = {}


def kogi_register_hook(key, runner, detector):
    if key is not None and runner is not None:
        RUNNER[key] = runner
    if detector is not None:
        DETECTOR.append(detector)


def kogi_run_cell(ipy, raw_cell, kwargs):
    directive = None
    result = None
    if '# kogi' in raw_cell:
        _, _, cmd = raw_cell.partition('# kogi')
        directive, _, _ = cmd.partition('\n')
    if directive is None and '#kogi' in raw_cell:
        _, _, cmd = raw_cell.partition('#kogi')
        directive, _, _ = cmd.partition('\n')
    if directive is not None:
        directive = directive.strip()
        for detector in DETECTOR:
            key = detector(directive, raw_cell)
            if key in RUNNER:
                result = RUNNER[key](ipy, raw_cell, directive)
                if not isinstance(result, ExecutionResult):
                    result = RUN_CELL(ipy, 'pass', **kwargs)
                return result
    if result is None:
        result = RUN_CELL(ipy, raw_cell, kwargs)
    return result


def change_run_cell(func):
    @wraps(func)
    def run_cell(*args, **kwargs):
        try:
            #args[1] is raw_cell
            return kogi_run_cell(args[0], args[1], kwargs)
        except:
            traceback.print_exc()
        value = func(*args, **kwargs)
        return value
    return run_cell


def change_showtraceback(func):
    @wraps(func)
    def showtraceback(*args, **kwargs):
        # print('** new version ***')
        # value = func(*args, **kwargs)
        try:
            ipyshell = args[0]
            code = ipyshell.user_global_ns['In'][-1]
            kogi_catch(code=code)
        except:
            traceback.print_exc()
    return showtraceback


def enable_kogi_hook():
    InteractiveShell.run_cell = change_run_cell(RUN_CELL)
    InteractiveShell.showtraceback = change_showtraceback(SHOW_TRACEBACK)
    InteractiveShell.showsyntaxerror = change_showtraceback(SHOW_SYNTAXERROR)


def disable_kogi_hook():
    InteractiveShell.run_cell = RUN_CELL
    InteractiveShell.showtraceback = SHOW_TRACEBACK
    InteractiveShell.showsyntaxerror = SHOW_SYNTAXERROR
