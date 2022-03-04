import sys
from IPython.core.magic import register_cell_magic

from .errors import corgi_translate_error
from .chat import corgi_chat

# _lines = None
# _outputs = None


def _run_fn(code, option):
    res = get_ipython().run_cell(code)
    res.raise_error()


def corgi_run(code, option, run_fn=_run_fn):
    # global _lines, _outputs
    try:
        run_fn(code, option)
    except:
        corgi_translate_error(code, return_html=True)
        corgi_chat()
    # finally:
    #     _lines = None
    #     _outputs = None


CORGI_OPTIONS = [
]


def corgi_add_option(isOption, runner):
    '''
    Example:
    isOption: lambda option: 'atcoder.com' in option
    return _run_fn
    '''
    CORGI_OPTIONS.append(isOption, runner)


def _corgi_check_option(option):
    for isOption, runner in CORGI_OPTIONS:
        if isOption(option):
            return runner
    return _run_fn


@register_cell_magic
def corgi(option, code):
    corgi_run(code, option, run_fn=_corgi_check_option(option))
