import linecache
import sys
import json
from  kogi.liberr.emodel import ErrorModel, extract_params_from_error

class KogiError(Exception):
    def __init__(self, **kw):
        Exception.__init__(self, json.dumps(kw))

_defaultErrorModel = ErrorModel('emsg_ja.txt')

def catch_exception(exc_info=None, code=None, include_locals=False, include_translated=True):
    if exc_info is None:
        etype, evalue, tb = sys.exc_info()
    else:
        etype, evalue, tb = exc_info
    emsg = (f"{etype.__name__}: {evalue}").strip()

    stacks = []
    stack_vars = []
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        if 'lib' not in filename:
            name = tb.tb_frame.f_code.co_name
            lineno = tb.tb_lineno
            line = linecache.getline(filename, lineno, tb.tb_frame.f_globals)
            local_vars = tb.tb_frame.f_locals
            stacks.append(dict(filename=filename,
                               etype=f'{etype.__name__}', emsg=emsg,
                               name=name, lineno=lineno, line=line))
            stack_vars.append(local_vars)
        tb = tb.tb_next
    results = dict(etype=f'{etype.__name__}',
                   emsg=emsg, traceback=list(stacks[::-1]))
    if code is not None:
        results['code'] = code
    if include_locals:
        results['locals'] = list(stack_vars[::-1])
    if include_translated:
        results.update(_defaultErrorModel.get_slots(emsg))
    return results
