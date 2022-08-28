import json
import os
import sys
import shlex
from base64 import b64encode
from binascii import a2b_base64
import traceback
import IPython

from ._google import google_colab

INSTALLED = False


def _install():
    global INSTALLED
    if not INSTALLED and google_colab:
        os.system('apt-get -y install imagemagick')
        os.system('apt-get -y install pngquant')
        INSTALLED = True


def _convert(file, width=None, height=None):
    if height is None:
        height = width*10 if width else None
    if width is None:
        width = height*10 if height else None
    if width and height:
        file2 = file.replace('.', '_.')
        os.system(f'convert -resize {width}x{height} {file} {file2}')
        os.remove(file)
        return file2
    return file


def toDataURL(file, mimetype):
    with open(file, 'rb') as f:
        bin = f.read()
    return f'data:{mimetype};base64,'+b64encode(bin).decode()


IMAGE_CACHE = {}


def wget(url, width=None, height=None):
    _install()
    if url in IMAGE_CACHE:
        return IMAGE_CACHE[url]
    qurl = shlex.quote(url)
    data_url = None
    if url.endswith('.png') or url.endswith('.PNG'):
        os.system(f'wget {qurl} -O im.png')
        if not os.path.exists('im.png'):
            return False
        file = _convert('im.png', width, height)
        file2 = file.replace('.png', '-fs8.png')
        os.system(f'pngquant {file}')
        os.remove(file)
        data_url = toDataURL(file2, 'image/png')
        os.remove(file2)
    if url.endswith('.jpg') or url.endswith('.jpeg'):
        os.system(f'wget {qurl} -O im.jpg')
        if not os.path.exists('im.jpg'):
            return False
        file = _convert('im.jpg', width, height)
        data_url = toDataURL(file, 'image/jpeg')
        os.remove(file)
    if data_url is None:
        return False
    IMAGE_CACHE[url] = data_url
    return data_url


def new_context(contexts=[]):
    class KParam(object):
        def __init__(self, name, value):
            nonlocal contexts
            self.name = name
            self.value = value
            contexts.append(self)

        def to_json(self):
            return (0, self.name, self.value)

    class KMethod(object):
        def __init__(self, name):
            self.name = name
            nonlocal contexts
            contexts.append(self)

        def __call__(self, *args):
            self.args = args

        def to_json(self):
            return (1, self.name, self.args)

    class Context(object):
        def __setattr__(self, name, value):
            KParam(name, value)
            return None

        def __getattr__(self, name):
            return KMethod(name)

    return Context()


CANVAS_HTML = '''
<canvas id="canvas" width="400" height="300" style="background-color:rgb(240,240,240)"></canvas>
'''

DRAW_JS = '''
const canvas = document.getElementById('canvas');
const draw = (data) => {
    if(data.length===0) {
        return;
    }
    const ctx = canvas.getContext('2d');
    for(const op of data) {
        if(op[0] === 0) {
            ctx[op[1]] = op[2];
        }
        else{
            if(op[1] === 'drawImage' && typeof op[2][0] === 'string') {
                console.log(op[2][0]);
                op[2][0] = document.getElementById(op[2][0]);
            }
            ctx[op[1]](...op[2]);
        }
    }
};
const redraw = (x, y, dataURL) => {
    (async function() {
    const result = await google.colab.kernel.invokeFunction(
        'notebook.redraw', // The callback name.
        [x, y, dataURL], // The arguments.
        {}); // kwargs
    const cdata = result.data['application/json'];
    draw(cdata.result);
    })();
};
var mouse = {x: 0, y: 0};
canvas.addEventListener('mousemove', function(e) {
  mouse.x = e.pageX - this.offsetLeft
  mouse.y = e.pageY - this.offsetTop
});
redraw(mouse.x, mouse.y, '');
'''

ANIME_JS = '''
var frame_index = 0;
const tm = setInterval(()=>{
    draw(data[frame_index]);
    frame_index = (frame_index + 1) % data.length;
}, 100);
'''

CLICK_JS = '''
canvas.onmousedown = ()=>{
  redraw(mouse.x, mouse.y, '');
}
'''

MOVIE_JS = '''
const frame_max = 1000;
var frame_index = 0;
const tm = setInterval(()=>{
    const dataURL = canvas.toDataURL();
    redraw(frame_index, frame_max, dataURL);
    frame_index += 1;
    if(frame_index >= frame_max) {
        clearInterval(tm);
    }
}, 500);
'''


def display_none(html):
    return f'<div style="display:none;">\n{html}\n</div>\n'


def safe(f):
    def safe_fn(*args):
        nonlocal f
        try:
            return f(*args)
        except:
            traceback.print_exc()
            return IPython.display.JSON({
                'result': []
            })
    return safe_fn


class Canvas(object):
    def __init__(self, width=400, height=300, framerate=5, onclick=None):
        self.width = width
        self.height = height
        self.images = {}
        self.buffers = []
        self.draw_fn = onclick
        self.time_index = 0
        self.filename = 'canvas.mp4'
        self.framerate = framerate
        if google_colab:
            google_colab.register_callback(
                'notebook.redraw', safe(self.redraw))

    def loadImage(self, image_key, url, width=None, height=None):
        self.images[image_key] = wget(url, width=width, height=height)

    def canvas_html(self):
        html = CANVAS_HTML.replace('400', f'{self.width}')
        html = html.replace('300', f'{self.height}')
        ss = []
        for key, data_url in self.images.items():
            ss.append(f'<img id="{key}" src="{data_url}">')
        return display_none('\n'.join(ss)) + html

    def canvas_js(self):
        js = DRAW_JS
        if len(self.buffers) > 0:
            data = [[c.to_json() for c in cb] for cb in self.buffers]
            data = json.dumps(data)
            js += f'const data = {data};\ndraw(data[0]);\n'
        if self.draw_fn:
            js += CLICK_JS
        else:
            js += ANIME_JS.replace('100', f'{1000//self.framerate}')
        return f'<script>\n{js}\n</script>'

    def _repr_html_(self):
        return self.canvas_html()+self.canvas_js()

    def getContext(self, target='2d'):
        cb = []
        self.buffers.append(cb)
        ctx = new_context(cb)
        ctx.clearRect(0, 0, self.width, self.height)
        return ctx

    def redraw_click(self, x, y):
        cb = []
        ctx = new_context(cb)
        ctx.clearRect(0, 0, self.width, self.height)
        self.draw_fn(ctx, self.time_index, self.width, self.height, x, y)
        self.time_index += 1
        return IPython.display.JSON({
            'result': [c.to_json() for c in cb]
        })

    def redraw(self, x=-1, y=-1, dataURI=''):
        if dataURI != '':
            return self.redraw_png(x, y, dataURI)
        if self.draw_fn is None:
            cb = self.buffers[0] if len(self.buffers) > 0 else []
            return IPython.display.JSON({
                'result': [c.to_json() for c in cb]
            })
        return self.redraw_click(x, y)

    def save_movie(self, filename=None, framerate=None):
        if filename is not None:
            self.filename = filename
        if framerate is not None:
            self.framerate = int(framerate)
        i = 0
        while True:
            fname = f'image{i:04d}.png'
            if not os.path.exists(fname):
                break
            os.remove(fname)
            i += 1
        max_iter = len(self.buffers)
        js = DRAW_JS+MOVIE_JS.replace('1000', f'{max_iter}')
        HTML = display_none(self.canvas_html())+f'<script>\n{js}\n</script>\n'
        display(IPython.display.HTML(HTML))

    def redraw_png(self, x, y, dataURI):
        _, _, dataURI = dataURI.partition("base64,")
        binary_data = a2b_base64(dataURI)
        fname = f'image{x:04d}.png'
        index = f'{x}/{y}'
        size = f'size={len(binary_data)}'
        print(f'[{index}] {fname} {size}')
        if google_colab:
            google_colab.clear(output_tags='outputs')
            with google_colab.use_tags('outputs'):
                sys.stdout.write(f'[{index}] {fname} {size}\n')
                sys.stdout.flush()
        else:
            print(f'[{index}] {fname} {size}')
        with open(fname, 'wb') as fd:
            fd.write(binary_data)
        if x + 1 == y:
            self._save_movie(self.filename, self.framerate)
        cb = self.buffers[x]
        return IPython.display.JSON({
            'result': [c.to_json() for c in cb]
        })

    def _save_movie(self, filename='canvas.mp4', framerate=15):
        filename2 = shlex.quote(filename)
        framerate = int(framerate)
        if os.path.exists(filename):
            os.remove(filename)
        os.system(
            f'ffmpeg -y -framerate {framerate} -i image%04d.png -vcodec libx264 -pix_fmt yuv420p {filename2}')
        if os.path.exists(filename):
            print(f'Saved {filename}')
            return MP4(filename, self.width)


class MP4(object):
    def __init__(self, filename, width=400):
        self.filename = filename
        self.width = width

    def _repr_html_(self):
        with open(self.filename, 'rb') as fd:
            bin = fd.read()
            data_url = "data:video/mp4;base64," + b64encode(bin).decode()
            return f'''
            <video width="{self.width}" controls >
            <source src="{data_url}" type="video/mp4" >
            </video >
            '''
