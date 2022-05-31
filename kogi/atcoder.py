
from IPython.core.magic import register_cell_magic
from .atcoder_impl import print, input, _check_atcoder, _run_judge

#kogi_add_option(_check_atcoder, _run_judge)


@register_cell_magic
def ac(option, code):
    _run_judge(code, option)

@register_cell_magic
def atcoder(option, code):
    _run_judge(code, option)
    #kogi_run(code, option, run_cell=_run_judge)
