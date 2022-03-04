from IPython.core.magic import register_cell_magic

from .chat import kogi_chat
from .errors import kogi_translate_error
from .atcoder import input, print, run_judge, check_atcoder

from .dialog import response_simply


def _run_cell(code, option):
    res = get_ipython().run_cell(code)
    res.raise_error()


def kogi_run(code, option, run_cell=_run_cell):
    try:
        run_cell(code, option)
    except:
        results = kogi_translate_error(code, return_html=True)
        if 'error_orig' in results:
            update_frame = {
                'reason': results.get('reason', None),
                'solution': results.get('solution', None),
                'hint': results.get('hint', None),
            }
            kogi_chat(results['error'], chat=response_simply,
                      update_frame=update_frame)
        else:
            update_frame = {
                'reason': '限界しか感じません',
                'solution': 'プログラミングが得意な新しい友達を作ろう',
                'hint': None,
            }
            kogi_chat('くーん', chat=response_simply, update_frame=update_frame)


KOGI_OPTIONS = [
    (check_atcoder, run_judge)
]


def _kogi_check_option(option):
    for isOption, runner in KOGI_OPTIONS:
        if isOption(option):
            return runner
    return _run_cell


@register_cell_magic
def kogi(option, code):
    kogi_run(code, option, run_cell=_kogi_check_option(option))


@register_cell_magic
def corgi(option, code):
    kogi_run(code, option, run_cell=_kogi_check_option(option))
