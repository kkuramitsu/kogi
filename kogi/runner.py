from IPython.core.magic import register_cell_magic

try:
    from .webui import kogi_say
except ModuleNotFoundError:
    pass

from .utils import print_nop
from .logger import kogi_print
from .dialog import get_chatbot
from .errors import kogi_check_error


KOGI_OPTIONS = [
]


def kogi_add_option(isOption, runner):
    KOGI_OPTIONS.append((isOption, runner))


def _run_cell(code, option):
    res = get_ipython().run_cell(code)
    res.raise_error()


def _kogi_check_option(option):
    for isOption, runner in KOGI_OPTIONS:
        if isOption(option):
            return runner
    return _run_cell


def kogi_run(code, option, run_cell=None):
    if run_cell is None:
        run_cell = _kogi_check_option(option)
    try:
        run_cell(code, option)
    except:
        results = kogi_check_error(code, show=print_nop, render_html=True)
        kogi_print(results)
        if 'error_orig' in results:
            kogi_say(results['error'], get_chatbot(results))
        else:
            kogi_say(('くぅーん'))


@register_cell_magic
def kogi(option, code):
    kogi_run(code, option)


@register_cell_magic
def corgi(option, code):
    kogi_run(code, option)
