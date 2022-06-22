import signal


def handler(signum, frame):
    #print("Timeout is over!")
    raise TimeoutError("Time Limit Exceeded")


signal.signal(signal.SIGALRM, handler)


class Timeout(object):
    def __init__(self, timeout=5):
        self.timeout = timeout

    def __enter__(self):
        signal.alarm(self.timeout)

    def __exit__(self, exc_type, exc_value, traceback):
        signal.alarm(0)  # cancel it


def eval_with_timeout(code, globals=None, locals=None, timeout=10):
    with Timeout(timeout):
        return eval(code, globals, locals)


def exec_with_timeout(code, globals=None, locals=None, timeout=10):
    with Timeout(timeout):
        exec(code, globals, locals)
