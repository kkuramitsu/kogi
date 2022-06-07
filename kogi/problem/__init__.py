from .judge import judge
from .atcoder import download_atcoder_data


def run_judge(run_cell, code):
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
            print('@@', url, data)
            judge(run_cell, code, data)
        else:
            print('**', url)
            run_cell(code)
