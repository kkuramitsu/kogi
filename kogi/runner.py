from .errors import kogi_check_error


def _run_cell(code, option):
    res = get_ipython().run_cell(code)
    res.raise_error()


KOGI_OPTIONS = [
]


def kogi_add_option(isOption, runner):
    KOGI_OPTIONS.append((isOption, runner))


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
        results = kogi_check_error(code, return_html=True)
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
