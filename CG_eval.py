import csv
import sys
import black
import Levenshtein
import nltk
#nltk.download('punkt')
from nltk import bleu_score
from io import BytesIO
from tokenize import tokenize, open
import re
from sumeval.metrics.rouge import RougeCalculator

import warnings
warnings.filterwarnings('ignore')

# def install(module):
#   try:
#       import module
#   except ModuleNotFoundError:
#       os.system(f'pip install {module}}')

def read_tsv(filename):
    ss = []
    with open(filename) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
          ss.append((row[index_id], row[pred_id]))
    return ss


def Exact_Match(ss):

  #print("<BLACK_NG>")
  
  #正答数
  correct=0

  #blackが使用できない数
  black_NG=0

  for line in ss:
    index=line[0]
    pred=line[1]

    try:
      index_black=black.format_str(index,mode=black.Mode())[:-1]
      pred_black=black.format_str(pred,mode=black.Mode())[:-1]

      if index_black==pred_black:
        correct+=1

    except:
      black_NG+=1
      #blackを利用した際にERRORが発生した箇所をテキストファイルに記入
      #with open('BLACK_NG.txt',mode='a') as f:
        #f.writelines(line)
        #f.write('\n')
      #print(line)

  #誤答数
  no_correct=len(ss)-correct

  #正答率
  correct_answer_rate=correct/len(ss)

  print("全体件数：",len(ss))
  print("BLACK_NG：",black_NG)
  print("正答数：",correct)
  print("誤答数：",no_correct)
  print("正答率：",round(correct_answer_rate,5))


def Levenstein(ss):

  #合計
  sum_Levenstein=0

  for line in ss:
    index=line[0]
    pred=line[1]
    sum_Levenstein += Levenshtein.ratio(index,pred)

  #平均値
  leven=sum_Levenstein/len(ss)
  
  print("leven：",round(leven,5))


def BLEU(ss):
  # https://www.nltk.org/api/nltk.translate.bleu_score.html

  pattern = re.compile(r'[\(, .\+\-\)]')

  def tokenize_pycode(code):
      try:
          ss=[]
          tokens = tokenize(BytesIO(code.encode('utf-8')).readline)
          for toknum, tokval, _, _, _ in tokens:
              if toknum != 62 and tokval != '' and tokval != 'utf-8':
                  ss.append(tokval)
          return ss
      except:
          return pattern.split(code)

  #合計
  sum_bleu = 0

  for line in ss:
    index=line[0]
    pred=line[1]
    sum_bleu += bleu_score.sentence_bleu([tokenize_pycode(index)],tokenize_pycode(pred))

     #平均値
  bleu = sum_bleu / len(ss)

  print("BLEU：",round(bleu,5))


def ROUGE_L(ss):

  rouge = RougeCalculator()
  sum_ROUGE_score=0

  for line in ss:
    index=line[0]
    pred=line[1]

    ROUGE_score = rouge.rouge_l(
            summary=pred,
            references=index)
    
    sum_ROUGE_score+=ROUGE_score
  #平均
  ROUGE_score=sum_ROUGE_score/len(ss)

  print("ROUGE-L：",round(ROUGE_score,5))

def arg():
  try:
    print(f"index = {sys.argv[2]}, pred = {sys.argv[3]}")
    return int(sys.argv[2]),int(sys.argv[3])
  except:
    print("index = 2, pred = 1")
    return 2, 1
    

def main():
  global index_id
  global pred_id

  index_id, pred_id = arg()
  
  ss = read_tsv(sys.argv[1])
  print(sys.argv[1])

  Exact_Match(ss)
  BLEU(ss)
  ROUGE_L(ss)
  Levenstein(ss)
  

main()

