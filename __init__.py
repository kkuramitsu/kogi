from IPython.core.magic import register_cell_magic

from .errors import corgi_translate_error
from .chat import corgi_chat
from .atcoder import input, print, run_judge, check_atcoder


def _run_cell(code, option):
    res = get_ipython().run_cell(code)
    res.raise_error()


def corgi_run(code, option, run_cell=_run_cell):
    try:
        run_cell(code, option)
    except:
        results = corgi_translate_error(code, return_html=True)
        if 'translated' in results:
            corgi_chat(results['translated'])
        else:
            corgi_chat('わん')


CORGI_OPTIONS = [
    (check_atcoder, run_judge)
]


def _corgi_check_option(option):
    for isOption, runner in CORGI_OPTIONS:
        if isOption(option):
            return runner
    return _run_cell


@register_cell_magic
def corgi(option, code):
    corgi_run(code, option, run_cell=_corgi_check_option(option))
