_CORGI_SIMPLE = True

def _simple(s):
    if '/' in s:
        return s.split('/')[0] if _CORGI_SIMPLE else s.split('/')[1]
    return s
