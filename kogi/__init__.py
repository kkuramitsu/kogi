
# try:
#     from .webui import kogi_login, kogi_help, kogi_translate, kogi_print
# except ModuleNotFoundError:
#     pass
#from .runner import kogi, corgi


try:
    from .exception_hook import enable_kogi_hook, disable_kogi_hook
    from .parse_error import DEBUG_ERR
    enable_kogi_hook()
except ModuleNotFoundError:
    pass
