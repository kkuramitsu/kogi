import linecache
import sys
import json
import traceback

from kogi.liberr.emodel import ErrorModel, extract_params_from_error


class KogiError(Exception):
    def __init__(self, **kw):
        Exception.__init__(self, json.dumps(kw))


_defaultErrorModel = ErrorModel('emsg_ja.txt')


def catch_exception(exc_info=None, code=None, include_translated=True, include_locals=False, local_vars={}, logging_json=None):
    if exc_info is None:
        etype, evalue, tb = sys.exc_info()
    else:
        etype, evalue, tb = exc_info
    emsg = (f"{etype.__name__}: {evalue}").strip()

    stacks = []
    stack_vars = []
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        if '<string>' in filename and code is not None:
            name = tb.tb_frame.f_code.co_name
            lineno = tb.tb_lineno
            lines = code.splitlines()
            line = lines[lineno-1].strip()
            stacks.append(dict(filename=filename,
                               etype=f'{etype.__name__}', emsg=emsg,
                               name=name, lineno=lineno, line=line))
            stack_vars.append(local_vars)
        elif 'lib' not in filename:
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
    if logging_json is not None:
        logging_json(
            type='exception_hook', code=code, emsg=emsg,
            traceback=results['traceback']
        )
    return results


def kogi_catch(exc_info=None, code: str = None, context: dict = None, dialog=None, logging_json=None):
    if exc_info is None:
        exc_info = sys.exc_info()
    slots = catch_exception(exc_info, code=code, logging_json=logging_json)
    if context is not None:
        slots.update(context)
    if dialog is None:
        print(slots)
    else:
        dialog(slots, logging_json=logging_json)


def print_exec_exception(code):
    etype, evalue, tb = sys.exc_info()
    emsg = (f"{etype.__name__}: {evalue}").strip()
    print(emsg)
    print('エラーが発生した箇所')
    lines = code.splitlines()
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        name = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno
        if '<string>' in filename:
            line = lines[lineno-1]
            print(f'line {lineno}, in {name}\n\t{line.strip()}')
            # "/Users/kimio/Git/kogi/kogi/problem/judge.py", line 47, in judge
        # else:
        #     line = linecache.getline(filename, lineno, tb.tb_frame.f_globals)
        #     print(f'{filename}, line {lineno} in {name}\n\t{line.strip()}')
        tb = tb.tb_next
