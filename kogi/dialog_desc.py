import os

DESC = None

# pardir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(pardir)


def load_descriptions():
    global DESC
    if DESC is None:
        # base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        # for file in os.listdir(base):
        #     if file.endswith(.csv)
        # pass
        DESC = {
            'コギー': 'プログラミング学習を補助してくれるAI犬',
            'プログラミング': '決して避けては通れない道',
            'データフレーム': 'Pandasで用いられる表形式のデータ',
            'イテラブル': 'for文などで繰り返し処理の対象になるオブジェクト',
        }
    return DESC


def response_desc(text):
    desc = load_descriptions()
    if text in desc:
        return text
    return 'わん'
