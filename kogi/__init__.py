from IPython.core.magic import register_cell_magic

from .webui import kogi_help, kogi_translate, kogi_login
from .runner import kogi_run, kogi_add_option
from .atcoder import input, print, _check_atcoder, _run_judge

kogi_add_option(_check_atcoder, _run_judge)


@register_cell_magic
def kogi(option, code):
    kogi_run(code, option)


@register_cell_magic
def corgi(option, code):
    kogi_run(code, option)
