
from kogi.logger import kogi_set, kogi_print

try:
    from .exception_hook import enable_kogi_hook, disable_kogi_hook
    enable_kogi_hook()
except ModuleNotFoundError as e:
    kogi_print('Only Available on Google Colab')
    pass
