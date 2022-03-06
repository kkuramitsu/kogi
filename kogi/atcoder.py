
from IPython.core.magic import register_cell_magic
from .runner import kogi_run, kogi_add_option
from .atcoder_impl import print, input, _check_atcoder, _run_judge

kogi_add_option(_check_atcoder, _run_judge)


@register_cell_magic
def atcoder(option, code):
    kogi_run(code, option, run_cell=_run_judge)
