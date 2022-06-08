import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup
SAMPLE = {}


def download_atcoder_data(url):
    if '?' in url:
        url, _, _ = url.rpartition('?')
    _, _, problem_id = url.rpartition('/')
    if problem_id in SAMPLE:
        return SAMPLE[problem_id]
    # try:
    try:
        response = requests.get(url)
    except Timeout:
        kogi_print('ネットの接続ができず、データがダウンロードできませんでした.')
        return {}

    if response.status_code == 404:
        return {}
    response_text = response.text
    html = BeautifulSoup(response_text, "lxml")
    d = {}
    for a in html.find_all("section"):
        # print(a)
        if a.h3 and a.pre:
            key = a.h3.text.replace('\r\n', '\n')
            value = a.pre.text.replace('\r\n', '\n')
            d[key] = value
    data = {'problem_id': problem_id, 'url': url}
    testcases = []
    if '入力例 1' in d:
        testcases.append(dict(input=d['入力例 1'], output=d['出力例 1']))
    if '入力例 2' in d:
        testcases.append(dict(input=d['入力例 2'], output=d['出力例 2']))
    if '入力例 3' in d:
        testcases.append(dict(input=d['入力例 3'], output=d['出力例 3']))
    data['testcases'] = testcases
    SAMPLE[problem_id] = data
    return data


if __name__ == '__main__':
    print(download_atcoder_data(
        'https://atcoder.jp/contests/abc204/tasks/abc204_z'))
