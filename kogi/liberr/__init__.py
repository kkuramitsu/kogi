# import linecache
# import sys
# import json
# import traceback

# from kogi.liberr.emodel import ErrorModel, extract_params_from_error
# from kogi.liberr.print_tb import kogi_print_exc, kogi_register_repr

from ._extract_emsg import extract_emsg, replace_eparams
from ._translate import translate_emsg, load_emsg_dic
from ._traceback import kogi_print_exc, kogi_register_repr


# class KogiError(Exception):
#     def __init__(self, **kw):
#         Exception.__init__(self, json.dumps(kw))


# _defaultErrorModel = ErrorModel('emsg_ja.txt')
# def catch_exception(exc_info=None, code=None, include_translated=True, include_locals=False, local_vars={}, logging_json=None):
#     if exc_info is None:
#         etype, evalue, tb = sys.exc_info()
#     else:
#         etype, evalue, tb = exc_info
#     emsg = (f"{etype.__name__}: {evalue}").strip()

#     stacks = []
#     stack_vars = []
#     eline = None
#     elineno = None
#     while tb:
#         filename = tb.tb_frame.f_code.co_filename
#         if '<string>' in filename and code is not None:
#             name = tb.tb_frame.f_code.co_name
#             elineno = tb.tb_lineno
#             lines = code.splitlines()
#             eline = lines[elineno-1].strip()
#             stacks.append(dict(filename=filename,
#                                etype=f'{etype.__name__}', emsg=emsg,
#                                name=name, lineno=elineno, line=eline))
#             stack_vars.append(local_vars)
#         elif 'lib' not in filename:
#             name = tb.tb_frame.f_code.co_name
#             lineno = tb.tb_lineno
#             line = linecache.getline(filename, lineno, tb.tb_frame.f_globals)
#             local_vars = tb.tb_frame.f_locals
#             stacks.append(dict(filename=filename,
#                                etype=f'{etype.__name__}', emsg=emsg,
#                                name=name, lineno=lineno, line=line))
#             stack_vars.append(local_vars)
#             if code is not None and line in code:
#                 elineno = lineno
#                 eline = line.strip()
#         tb = tb.tb_next
#     results = dict(etype=f'{etype.__name__}',
#                    emsg=emsg, traceback=list(stacks[::-1]))
#     if code is not None:
#         results['code'] = code
#     if include_locals:
#         results['locals'] = list(stack_vars[::-1])
#     if include_translated:
#         results.update(_defaultErrorModel.get_slots(emsg))
#     if logging_json is not None:
#         logging_json(
#             type='exception_hook',
#             code=code, emsg=emsg,
#             traceback=results['traceback'],
#             elineno=elineno, eline=eline
#         )
#     return results
