import uuid
import json
from datetime import datetime

verbose = True


def kogi_verbose(enabled: bool):
    global verbose
    verbose = enabled


def kogi_print(*args, **kw):
    global verbose
    if verbose:
        print('\033[35m[🐶]', *args, **kw)
        print('\033[0m', end='')


def print_nop(*x):
    pass

## LOGGER

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
        local_slack =  Slack(url)
        if update:
            slack = local_slack
    except Exception as e:
        print('Slack Error', e)
    return local_slack
    

def send_slack(logs, slack_id='QNZDoUPuLo7C3lHyh9PWhZz3'):
    try:
        local_slack = load_slack(slack_id=slack_id, update=False)
        jsondata = json.dumps(logs, ensure_ascii=False)
        local_slack.notify(text = jsondata)
    except Exception as e:
        print('Slack Error:', e)



SESSION = str(uuid.uuid1())
SEQ = 0
LOGS = []
UID = 'unknown'
epoch = datetime.now().timestamp()

def check_logging():
    if len(LOGS) > 32: 
        return True

def send_log(right_now=False, print=kogi_print):
    global epoch, LOGS
    try:
        now = datetime.now().timestamp()
        delta = (now - epoch)
        epoch = now
        if len(LOGS) > 0 and (right_now or delta > 180):
            data = LOGS.copy()
            LOGS.clear()
            data = json.dumps(data, ensure_ascii=False)
            if slack is not None:
                slack.notify(text=data)
            else:
                print(data)
    except Exception as e:
        kogi_print(e)

def log(**kw):
    global SEQ, LOGS, epoch
    now = datetime.now()
    date = now.isoformat(timespec='seconds')
    logdata = dict(session=SESSION, seq=SEQ, uid=UID, date=date, **kw)
    LOGS.append(logdata)
    SEQ += 1
    send_log()
    return logdata

def record_login(uid, **kw):
    global UID
    UID = f'{uid}'
    logdata = log(**kw)
    if slack is None:
        send_slack(logdata)
        

if __name__ == '__main__':
    # log(a=1, b=2)
    # log_now()
    record_login(uid='11111', test='test')
