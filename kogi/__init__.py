
import traceback
from kogi.logger import kogi_set, kogi_print

try:
    from .exception_hook import enable_kogi_hook, disable_kogi_hook
    enable_kogi_hook()
except ModuleNotFoundError as e:
    # traceback.print_exc()
    kogi_print('Only Available on Google Colab')
    pass
