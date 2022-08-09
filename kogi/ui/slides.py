from IPython.display import display, HTML
from IPython.core.magic import register_line_magic

# https://docs.google.com/presentation/d/e/2PACX-1vR96clROL-GKBYq5LwREjOmpryFHLULrbaikjEs3-CecbuDqMFO9-MAZPD2_VY6SWiJZMsRaHPeWjCV

URL = 'https://docs.google.com/presentation/d/e/{}'

SLIDE_HTML = '''
<iframe src="{}/embed?start=false&loop=true&delayms=3000" 
    frameborder="0" width="720" height="430" 
    allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true">
</iframe>
'''


@register_line_magic
def slide(line):
    if not line.startswith('https://'):
        line = URL.format(line)
    display(HTML(SLIDE_HTML.format(line)))
