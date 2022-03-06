
try:
    from .webui import kogi_login, kogi_help, kogi_translate
except ModuleNotFoundError:
    pass

from .runner import kogi, corgi
#from .atcoder import input, print, _check_atcoder, _run_judge
#kogi_add_option(_check_atcoder, _run_judge)
