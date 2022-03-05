
import sys
from nmt_compose import compose


def get_nmt(beams=1):
    return compose()


if __name__ == '__main__':
    nmt = get_nmt()
    for a in sys.argv[1:]:
        print(a, nmt(a))
