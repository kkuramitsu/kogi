from IPython.core.magic import register_cell_magic

from .errors import corgi_translate_error
from .chat import corgi_chat
from .atcoder import input, print, run_judge, check_atcoder

from .dialog import response_simply


def _run_cell(code, option):
    res = get_ipython().run_cell(code)
    res.raise_error()


def corgi_run(code, option, run_cell=_run_cell):
    try:
        run_cell(code, option)
    except:
        results = corgi_translate_error(code, return_html=True)
        if 'error_orig' in results:
            update_frame = {
                'reason': results.get('reason', None),
                'solution': results.get('solution', None),
                'hint': results.get('hint', None),
            }
            corgi_chat(results['error'], chat=response_simply,
                       update_frame=update_frame)
        else:
            update_frame = {
                'reason': '限界しか感じません',
                'solution': 'プログラミングが得意な新しい友達を作ろう',
                'hint': None,
            }
            corgi_chat('くーん', chat=response_simply, update_frame=update_frame)


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
