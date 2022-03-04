import uuid
import json
import builtins

try:
    from slackweb import Slack
    HOST = 'slack.com',
    ID = 'T02NYCBFP7B',
    ID2 = 'B02P9F4K5NU',
    ID3 = 'gAuxsB8pTCSXXI6tmRaduWBi',
    URL = f'https://hooks.{HOST}/services/{ID}/{ID2}/{ID3}',
    slack = Slack(URL)
except ModuleNotFoundError:
    slack = None


def print_nop(*x):
    pass


SESSION = str(uuid.uuid1())
seq = 0
LOGS = []


def log(**kw):
    global seq
    log = dict(session=SESSION, seq=seq, **kw)
    LOGS.append(log)
    seq += 1


def lognow(print=print_nop):
    global LOGS
    try:
        if len(LOGS) > 0:
            data = LOGS.copy()
            LOGS.clear()
            data = json.dumps(data, ensure_ascii=False)
            print(data)
            if slack is not None:
                slack.notify(text=data)
    except Exception as e:
        builtins.print(e)


if __name__ == '__main__':
    log(a=1, b=2)
    lognow(print=print)
