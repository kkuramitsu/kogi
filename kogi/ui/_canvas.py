import os
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
    const ctx = canvas.getContext('2d');
    for(const op of data) {
        if(op[0] === 0) {
            ctx[op[1]] = op[2];
        }
        else{
            if(op[1] === 'drawImage') {
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

CLICK_JS = '''
canvas.onmousedown = ()=>{
  redraw(mouse.x, mouse.y, '');
}
'''

ANIME_JS = '''
const frame_max = 100;
var frame_index = 0;
const tm = setInterval(()=>{
    redraw(mouse.x, mouse.y, '');
    frame_index += 1;
    if(frame_index >= frame_max) {
        clearInterval(tm);
    }
}, 500);
'''

MOVIE_JS = '''
const frame_max = 10;
var frame_index = 0;
const tm = setInterval(()=>{
    const dataURL = canvas.toDataURL();
    redraw(mouse.x, mouse.y, dataURL);
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
    def __init__(self, width=400, height=300, delay=500, onclick=None):
        self.width = width
        self.height = height
        self.images = {}
        self.buffers = []
        self.draw_fn = onclick
        self.time_index = 0
        self.delay = delay
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
        if self.draw_fn is not None:
            js += CLICK_JS
        if len(self.buffers) > 0 and self.delay > 100:
            js += ANIME_JS.replace('500', f'{self.delay}')
        return f'<script>\n{js}\n</script>'

    def _repr_html_(self):
        return self.canvas_html()+self.canvas_js()

    def getContext(self, target='2d'):
        cb = []
        self.buffers.append(cb)
        ctx = new_context(cb)
        ctx.clearRect(0, 0, self.width, self.height)
        return ctx

    def redraw0(self, x=-1, y=-1):
        size = len(self.buffers)
        if self.time_index < size:
            cb = self.buffers[self.time_index]
            self.time_index = (self.time_index+1) % size
        else:
            cb = []
        return IPython.display.JSON({
            'result': [c.to_json() for c in cb]
        })

    def redraw1(self, x=-1, y=-1):
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
        if len(self.buffers) > 0 or self.draw_fn is None:
            return self.redraw0(x, y)
        return self.redraw1(x, y)

    def redraw_png(self, x=-1, y=-1, dataURI=''):
        _, _, dataURI = dataURI.partition("base64,")
        binary_data = a2b_base64(dataURI)
        fname = f'image{self.time_index:04d}.png'
        print(fname, len(binary_data), self.time_index)
        with open(fname, 'wb') as fd:
            fd.write(binary_data)
        return self.redraw0(x, y)

    def save_to_mp4(self, filename='canvas.mp4', framerate=30):
        max_iter = len(self.buffers)+1
        js = DRAW_JS+MOVIE_JS.replace('1000', f'{max_iter}')
        HTML = display_none(self.canvas_html())+f'<script>\n{js}\n</script>\n'
        display(IPython.display.HTML(HTML))
        self.filename = filename
        self.framerate = int(framerate)

    def _show_mp4(self):
        filename = shlex.quote(self.filename)
        framerate = int(framerate)
        os.system(
            f'ffmpeg -framerate {framerate} -i image%04d.png -vcodec libx264 -pix_fmt yuv420p -r 60 {filename2}')
        if os.path.exists(filename):
            print(f'Saved {self.filename}')
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
