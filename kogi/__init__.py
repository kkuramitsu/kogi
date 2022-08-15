
from .settings import kogi_set, kogi_print
from .ui.slides import slide

set = kogi_set
print = kogi_print

try:
    from .exception_hook import enable_kogi_hook, kogi_register_hook
    enable_kogi_hook()
    from .problem import atcoder_detector, atcoder_judge
    kogi_register_hook('atcoder', atcoder_judge, atcoder_detector)
    from .ui import rmt
except ModuleNotFoundError as e:
    import traceback
    traceback.print_exc()
    kogi_print('Only Available on Google Colab')
    pass
