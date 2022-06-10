
from kogi.logger import kogi_set, kogi_print

try:
    from .exception_hook import enable_kogi_hook, disable_kogi_hook
    from .dialog import kogi_catch
    from kogi.problem import run_judge
    enable_kogi_hook(run_judge, kogi_catch)
except ModuleNotFoundError as e:
    kogi_print('Only Available on Google Colab')
    pass
