import sys
from IPython.core.magic import register_cell_magic

from .errors import kogi_translate_error
from .webui import kogi_chat

# _lines = None
# _outputs = None


def _run_fn(code, option):
    res = get_ipython().run_cell(code)
    res.raise_error()


def kogi_run(code, option, run_fn=_run_fn):
    # global _lines, _outputs
    try:
        run_fn(code, option)
    except:
        kogi_translate_error(code, render_html=True)
        kogi_chat()
    # finally:
    #     _lines = None
    #     _outputs = None


kogi_OPTIONS = [
]


def kogi_add_option(isOption, runner):
    '''
    Example:
    isOption: lambda option: 'atcoder.com' in option
    return _run_fn
    '''
    kogi_OPTIONS.append(isOption, runner)


def _kogi_check_option(option):
    for isOption, runner in kogi_OPTIONS:
        if isOption(option):
            return runner
    return _run_fn


@register_cell_magic
def kogi(option, code):
    kogi_run(code, option, run_fn=_kogi_check_option(option))
