import traceback
from kogi.logger import kogi_print
from .judge import judge
from .atcoder import download_atcoder_data


def run_judge(code):
    try:
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
                kogi_print('コギーがAtCoderを探知し、テストケースを実行しました')
                judge(code, data)
                return 'pass\n'
        return code
    except:
        traceback.print_exc()
    return code
