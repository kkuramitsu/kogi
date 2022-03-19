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


JUDGE_CSS = '''
<style>
.parent {
  background-color: #edebeb;
  width: 100%;
  height: 150px;
}
textarea {
  width: 100%; 
  box-sizing: border-box;  /* ※これがないと横にはみ出る */
  height:120px; 
  font-size: large;
  outline: none;           /* ※ブラウザが標準で付加する線を消したいとき */
  resize: none;
}
.box11{
//    padding: 0.5em 1em;
//    margin: 2em 0;
    color: #5d627b;
    background: white;
    border-top: solid 5px #5d627b;
    box-shadow: 0 3px 5px rgba(0, 0, 0, 0.22);
}
.box18{
  //padding: 0.2em 0.5em;
  //margin: 2em 0;
  color: #565656;
  background: #ffeaea;
  background-size: 150%;
  background-repeat: no-repeat;
  background-position: top right;
  background-color:rgba(255,255,255,0.8);
  background-blend-mode:lighten;
  //box-shadow: 0px 0px 0px 10px #ffeaea;
  border: dashed 2px #ffc3c3;
  //border-radius: 8px;
}
.box16{
    //padding: 0.5em 1em;
    //margin: 2em 0;
    background: -webkit-repeating-linear-gradient(-45deg, #f0f8ff, #f0f8ff 3px,#e9f4ff 3px, #e9f4ff 7px);
    background: repeating-linear-gradient(-45deg, #f0f8ff, #f0f8ff 3px,#e9f4ff 3px, #e9f4ff 7px);
}
.box24 {
    position: relative;
    padding: 0.5em 0.7em;
    margin: 2em 0; background: #6f4b3e;
    color: white; font-weight: bold;
}
.box24:after {
    position: absolute;
    content: '';
    top: 100%; left: 30px;
    border: 15px solid transparent;
    border-top: 15px solid #6f4b3e;
    width: 0; height: 0;
}
</style>
'''

JUDGE_HTML = '''
<div class="parent">
<h4>{title}</h4>
<pre>{input}</pre>
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="input">実行結果</label>
<textarea id="input" class="box16" readonly>{output}</textarea>
</div>
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="outout">正解例</label>
<textarea id="output" class="box18" readonly>{sample}</textarea>
</div>
</div>
'''


def _run_judge(code, problem):
    global _lines, _outputs
    d = _get_sample(problem)
    try:
        display(HTML(JUDGE_CSS))
        for key in ['入力例 1', '入力例 2', '入力例 3']:
            if key not in d:
                continue
            data = {'title': key, 'input': d[key]}
            # display(HTML(sample_html))
            _lines = [s for s in d[key].split('\n') if len(s) > 0]
            _outputs = []
            res = get_ipython().run_cell(code)
            res.raise_error()
            key = key.replace('入力', '出力')
            data['sample'] = d[key]
            data['output'] = ''.join(_outputs)
            display(HTML(JUDGE_HTML.format(**data)))
            # if result != output_example:
            #     ratio = difflib.SequenceMatcher(
            #         None, result, output_example).ratio()
            #     display(HTML(
            #         f'<h4>{key}(正解)</h4><pre style="background: #eee">{d[key]}</pre>'))
            #     if ratio > 0.8:
            #         _display_diff(output_example, result)
            # else:
            #     pass
            #     #display(HTML('<h4 style="color: green">✔︎</h4>'))
    finally:
        _lines = None
        _outputs = None
