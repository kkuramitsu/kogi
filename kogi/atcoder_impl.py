import difflib
import requests
from bs4 import BeautifulSoup
import builtins
from IPython.display import display, HTML

_lines = None
_outputs = None


def input(s=''):
    global _lines
    if _lines is not None and len(_lines) > 0:
        return _lines.pop(0)
    else:
        _lines = None
    return builtins.input(s)


def print(*a, **kw):
    builtins.print(*a, **kw)
    if _outputs is not None:
        sep = kw.get('sep', ' ')
        end = kw.get('end', '\n')
        s = sep.join([str(s) for s in a]) + end
        _outputs.append(s)


SAMPLE = {}


def _get_sample(problem):
    if '/' in problem:
        problem = problem[problem.rfind('/')+1:]
    problem = problem.lower()
    if '_' in problem:
        problem, num = problem.split('_')
    else:
        num = problem[-1]
        problem = problem[:-1]
    pid = f'{problem}_{num}'
    if pid in SAMPLE:
        return SAMPLE[pid]
    response_text = requests.get(
        url=f"https://atcoder.jp/contests/{problem}/tasks/{problem}_{num}").text
    html = BeautifulSoup(response_text, "lxml")
    d = {}
    for a in html.find_all("section"):
        # print(a)
        if a.h3 and a.pre:
            key = a.h3.text.replace('\r\n', '\n')
            value = a.pre.text.replace('\r\n', '\n')
            d[key] = value
    SAMPLE[pid] = d
    return d


def _check_atcoder(option):
    try:
        if 'atcoder' in option:
            d = _get_sample(option)
            return True
    except Exception as e:
        print('問題が読み込めません', e)
    return False


_COLOR_HTML_DIC = {
    'yellow': '<span style="background: pink">',
    'red': '<span style="background: lightblue">',
    'end': '</span>'
}


def _display_diff(ground_truth, target):
    _CDIC = _COLOR_HTML_DIC

    if ground_truth == target:
        return

    d = difflib.Differ()
    diffs = d.compare(ground_truth, target)

    result = ''
    for diff in diffs:
        status, _, character = list(diff)
        if status == '-':
            character = _CDIC['red'] + character + _CDIC['end']
        elif status == '+':
            character = _CDIC['yellow'] + character + _CDIC['end']
        else:
            pass
        result += character

    display(
        HTML(f'<h4>差分</h4><div style="white-space: pre-wrap;">{result}</div>'))


def _run_judge(code, problem):
    global _lines, _outputs
    d = _get_sample(problem)
    sample_html = None
    try:
        for key in ['入力例 1', '入力例 2', '入力例 3']:
            if key not in d:
                continue
            sample_html = f'<h4>{key}</h4><pre style="background: #ddd">{d[key]}</pre>'
            display(HTML(sample_html))
            _lines = [s for s in d[key].split('\n') if len(s) > 0]
            _outputs = []
            res = get_ipython().run_cell(code)
            res.raise_error()
            key = key.replace('入力', '出力')
            output_example = d[key]
            result = ''.join(_outputs)
            if result != output_example:
                ratio = difflib.SequenceMatcher(
                    None, result, output_example).ratio()
                display(HTML(
                    f'<h4>{key}(正解)</h4><pre style="background: #eee">{d[key]}</pre>'))
                if ratio > 0.8:
                    _display_diff(output_example, result)
            else:
                pass
                #display(HTML('<h4 style="color: green">✔︎</h4>'))
    finally:
        _lines = None
        _outputs = None
