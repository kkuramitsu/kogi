_kogi_SIMPLE = True


def _simple(s):
    if '/' in s:
        return s.split('/')[0] if _kogi_SIMPLE else s.split('/')[1]
    return s
