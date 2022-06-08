import uuid
import json
from datetime import datetime
import requests

# kogi global settings

kogi_globals = {}


def kogi_set(**kwargs):
    global kogi_globals
    kogi_globals.update(kwargs)


def kogi_print(*args, **kw):
    global kogi_globals
    if kogi_globals.get('verbose', True):
        print('\033[35m[🐶]', *args, **kw)
        print('\033[0m', end='')


def print_nop(*x, **kw):
    pass

# LOGGER


slack = None


def load_slack(slack_id='QNZDoUPuLo7C3lHyh9PWhZz3', update=True):
    global slack
    if slack_id is None:
        slack = None
        return None
    try:
        from slackweb import Slack
    except ModuleNotFoundError:
        import os
        os.system('pip install slackweb')
        from slackweb import Slack
    HOST = 'slack.com'
    ID = 'T02NYCBFP7B'
    ID2 = 'B02QPM8HNBH'
    if '/' not in slack_id:
        url = f'https://hooks.{HOST}/services/{ID}/{ID2}/{slack_id}'
    else:
        url = f'https://hooks.{HOST}/services/{slack_id}'
    try:
        local_slack = Slack(url)
        if update:
            slack = local_slack
    except Exception as e:
        print('Slack Error', e)
    return local_slack


def send_slack(logs, slack_id='QNZDoUPuLo7C3lHyh9PWhZz3'):
    try:
        local_slack = load_slack(slack_id=slack_id, update=False)
        jsondata = json.dumps(logs, ensure_ascii=False)
        local_slack.notify(text=jsondata)
    except Exception as e:
        print('Slack Error:', e)


SESSION = str(uuid.uuid1())
SEQ = 0
LOGS = []
UID = 'unknown'
KEY = 'OjwoF3m0l20OFidHsRea3ptuQRfQL10ahbEtLa'
epoch = datetime.now().timestamp()


def send_log(right_now=False, print=kogi_print):
    global epoch, LOGS
    url = 'https://ixe8peqfii.execute-api.ap-northeast-1.amazonaws.com/dev'
    now = datetime.now().timestamp()
    delta = (now - epoch)
    epoch = now
    if len(LOGS) > 0 and (right_now or delta > 180):
        data = {
            "session": SESSION,
            "uid": UID,
            "logs": LOGS.copy(),
        }
        LOGS.clear()
        headers = {'x-api-key': f'A{KEY}s'}
        r = requests.post(url, headers=headers, json=data)
        if r.status_code != 200:
            print(data)


def log(**kw):
    global SEQ, LOGS, epoch
    now = datetime.now()
    date = now.isoformat(timespec='seconds')
    logdata = dict(seq=SEQ, date=date, **kw)
    LOGS.append(logdata)
    SEQ += 1
    send_log()
    return logdata


def logging_json(**kw):
    global SEQ, LOGS, epoch
    now = datetime.now()
    date = now.isoformat(timespec='seconds')
    logdata = dict(seq=SEQ, date=date, **kw)
    LOGS.append(logdata)
    SEQ += 1
    send_log()
    return logdata


def record_login(uid, **kw):
    global UID
    UID = f'{uid}'
    logdata = log(uid=UID, **kw)
    send_log(right_now=True)
    if slack is None:
        send_slack(logdata)


if __name__ == '__main__':
    # log(a=1, b=2)
    # log_now()
    record_login(uid='11111', test='test')
