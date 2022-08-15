import time
import traceback
from .content import ICON, JS, CSS
from IPython.display import display, HTML, JSON
from kogi.settings import kogi_log, translate_en, model_generate, print_nop

try:
    from google.colab import output as colab_output
except ModuleNotFoundError:
    colab_output = None

RMT_HTML = '''
<div id="{id}" class="parent">
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="input">{input}</label>
<textarea id="input" class="box16"></textarea>
</div>
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="outout">{output}</label>
<textarea id="output" class="box18" readonly></textarea>
</div>
</div>
'''


def display_rmt(input='入力', output='出力', delay=600):
    data = dict(
        id=1,
        input=input,
        output=output,
        delay=600,
    )
    DHTML = RMT_HTML.format(**data)
    display(HTML(CSS('_rmt.css')+DHTML+JS('_rmt.js')))
    return id


class TransformWeaver(object):
    def before(self, text):
        return text

    def after(self, text):
        return text


TransformWeaverNone = TransformWeaver()


def codegen(text):
    if '<nl>' in text:
        text = text.replace('<nl>', '\n').replace('<tab>', '\t')
    return text


_LOGS = []


def rmt(input='入力', output='予測', delay=600, print=print_nop,
        transform=TransformWeaverNone, generate=model_generate):
    display_rmt(input=input, output=output, delay=delay)

    cached = {'': ''}

    def convert(text):
        global _LOGS
        try:
            ss = []
            for line in text.splitlines():
                if line not in cached:
                    _line = transform.before(line)
                    s = time.time()
                    _translated = generate(_line)
                    e = time.time()
                    _translated = codegen(_translated)
                    translated = transform.after(_translated)
                    print(f'{e-s:.3f}', line, '=>', translated)
                    if line == _line and translated == _translated:
                        _LOGS.append((line, translated))
                    else:
                        _LOGS.append((line, translated, _line, _translated))
                    cached[line] = translated
                else:
                    translated = cached[line]
                ss.append(translated)
            text = '\n'.join(ss)
            return JSON({'result': text})
        except:
            traceback.print_exc()

    def logger():
        global _LOGS
        if len(_LOGS) > 0:
            kogi_log('rmt', pairs=_LOGS)
            _LOGS = []

    if colab_output is not None:
        colab_output.register_callback('notebook.Convert', convert)
        colab_output.register_callback('notebook.Logger', logger)
