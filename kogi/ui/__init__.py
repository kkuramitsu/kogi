import base64
from IPython.display import display, HTML

import os
# import shutil


# def install_nbextensions(src_path, dist_path='/usr/local/share/jupyter/nbextensions/google.colab/'):
#     for file in os.listdir(src_path):
#         file = os.path.abspath(file)
#         print(file)
#         if file.endswith('.js') or file.endswith('.css'):
#             # shutil.copy(file, dist_path)
#             pass

_cache = {}


def load(file):
    file = f'{os.path.dirname(os.path.abspath(__file__))}/{file}'
    try:
        if file.endswith('.png'):
            file_data = open(file, "rb").read()
            return 'data:image/png;base64,' + base64.b64encode(file_data).decode('utf-8')
        else:
            with open(file) as f:
                return f.read()
    except:
        print(file)
        return


def ICON(file):
    if '/' in file:
        return file
    if file not in _cache:
        _cache[file] = load(file)
    return _cache[file]


def CSS(file):
    assert file.endswith('.css')
    if file not in _cache:
        _cache[file] = load(file)
    data = _cache[file]
    return f'<style>{data}</style>'


def JS(file):
    assert file.endswith('.js')
    if file not in _cache:
        _cache[file] = load(file)
    data = _cache[file]
    return f'<script>{data}</script>'


_DIALOG_BOT = '''
<div class="sb-box">
    <div class="icon-img icon-img-left">
        <img src="{icon}" width="60px">
    </div>
    <div class="icon-name icon-name-left">{name}</div>
    <div class="sb-side sb-side-left">
        <div class="sb-txt sb-txt-left">{text}</div>
    </div>
</div>
'''

_DIALOG_USER = '''
<div class="sb-box">
    <div class="icon-img icon-img-left">
        <img src="{icon}" width="60px">
    </div>
    <div class="icon-name icon-name-left">{name}</div>
    <div class="sb-side sb-side-left">
        <div class="sb-txt sb-txt-left">{text}</div>
    </div>
</div>
'''

SCRIPT = '''
<script>
var target = document.getElementById('{target}');
var content = `{html}`;
if(target !== undefined) {{
    target.insertAdjacentHTML('beforeend', content);
    target.scrollTop = target.scrollHeight;
}}
</script>
'''


def append_content(target, html):
    display(HTML(SCRIPT.format(target=target, html=html)))


def kogi_print(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    data = dict(
        text=sep.join([str(s) for s in args]),
        icon='kogi-fs8.png',
        name='コギー',
    )
    data.update(kwargs)
    data['icon'] = ICON(data.get('icon', '/'))
    _HTML = kwargs.get('html', _DIALOG_BOT)
    html = _HTML.format(**data)
    if 'target' in kwargs:
        target = kwargs['target']
        print('target', target)
        append_content(target, html=html)
    else:
        display(HTML(CSS('dialog.css') + html))


_DIALOG_MAIN = '''
<div id='dialog'>
    {script}
    <div id='output' class='box'>
    </div>
    <div style='text-align: right'>
        <textarea id='input' placeholder='{placeholder}'></textarea>
    </div>
</div>
'''


def display_dialog(placeholder='質問はこちらに'):
    data = dict(
        script=JS('dialog.js'),
        placeholder=placeholder
    )
    display(HTML(CSS('dialog.css') + _DIALOG_MAIN.format(**data)))

    def dialog_bot(bot_text, **kwargs):
        data = dict(
            icon='kogi-fs8.png',
            name='コギー',
            target='output'
        )
        data.update(kwargs)
        kogi_print(bot_text, **data)

    def dialog_user(user_text, **kwargs):
        data = dict(
            icon='kogi-fs8.png',
            name='あなた',
            html=_DIALOG_USER,
            target='output'
        )
        data.update(kwargs)
        kogi_print(user_text, **data)

    return dialog_bot, dialog_user


class Deco(object):

    def bold(self, text):
        return f'<b>{text}</b>'

    def code(self, text):
        return f'<code>{text}</code>'
