

def get_target(code):
    for c in code.splitlines()[::-1]:
        if '_ =' in c:
            return c.replace('_ =', '').strip()
        if '_=' in c:
            return c.replace('_=', '').strip()
    return ''

def run_tests(ref_code, user_code, tests):
    ref_vars = {}
    user_vars = {}
    exec(ref_code, None, ref_vars)
    exec(user_code, None, user_vars)
    
    for test in tests:
        print(get_target(test))
        exec(test, ref_vars, ref_vars)
        exec(test, user_vars, user_vars)
        ref_result = ref_vars['_']
        user_result = user_vars['_']
        print('result:', ref_result, user_result)

