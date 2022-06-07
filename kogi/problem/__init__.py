from .judge import judge
from .atcoder import download_atcoder_data


def run_judge(code):
    url = None
    for line in code.splitlines():
        if '#' in line and 'https://atcoder.jp/contests/' in line:
            _, urlbase, problem = line.partition(
                'https://atcoder.jp/contests/')
            url = urlbase + problem.strip()
            break
    if url is not None:
        data = download_atcoder_data(url)
        if 'problem_id' in data:
            judge(code, data)
            return 'pass\n'
        else:
            print('URLから問題文が読めません')
            return code
