import re
import json
from konlpy.tag import Okt
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import sys
import os
import io  # io 모듈 추가

# Okt 인스턴스와 토크나이저 설정 파일, 모델 로드 한 번만 실행
okt = Okt()
with open('data/tokenizer_config.json', 'r', encoding='utf-8') as f:
  tokenizer_config = json.load(f)
tokenizer = tokenizer_from_json(tokenizer_config)

model_path = 'data/best_model_adj.keras'
model = load_model(model_path)
max_len = 100

def sentiment_predict(new_sentence):
  new_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]', '', new_sentence)
  pos_sentence = okt.pos(new_sentence)  # 형태소 분석
  new_sentence = [okt.morphs(word, stem=True)[0] for word, pos in pos_sentence if pos == 'Adjective']  # 형용사의 어간 추출

  encoded = tokenizer.texts_to_sequences([new_sentence])  # 정수 인코딩
  if not encoded[0]:  # 빈 시퀀스 검사
    print("Warning: Empty sequence after tokenization.")
  pad_new = pad_sequences(encoded, maxlen=max_len)  # 패딩

  score = float(model.predict(pad_new))  # 예측
  return score

def analyze_reviews(reviews):
  from collections import defaultdict

  # 산별로 리뷰를 그룹화하기 위한 딕셔너리
  mountain_reviews = defaultdict(list)

  # 리뷰 데이터를 산별로 그룹화
  for review_data in reviews:
    mntnCode = review_data['mntnCode']
    mountain_reviews[mntnCode].append(review_data)

  results = []
  # 산의 개수를 계산하기 위한 변수
  total_mountains_count = len(mountain_reviews)

  # 산별로 긍정률과 부정률을 계산
  for mntnCode, reviews in mountain_reviews.items():
    positive_sum = 0
    negative_sum = 0
    for review_data in reviews:
      review = review_data['bcontent']
      score = sentiment_predict(review)
      positive_rate = score * 100
      negative_rate = (1 - score) * 100
      positive_sum += positive_rate
      negative_sum += negative_rate
      results.append({
        'mntnCode': mntnCode,
        'review': review,
        'positive_rate': positive_rate,
        'negative_rate': negative_rate
      })
      print("Prediction score:", score)  # 로깅 추가
      print("Prediction positive_rate:", positive_rate)  # 로깅 추가
      print("Prediction negative_rate:", negative_rate)  # 로깅 추가

    total_reviews = len(reviews)
    if total_reviews > 0:
      average_positive = positive_sum / total_reviews
      average_negative = negative_sum / total_reviews
    else:
      average_positive = 0
      average_negative = 0

    # 산별 평균 결과 추가
    results.append({
      'mntnCode': mntnCode,
      'total_reviews': total_reviews,
      'average_positive_rate': average_positive,
      'average_negative_rate': average_negative
    })

  # 산의 총 개수를 결과에 추가
  results.append({
    'total_mountains': total_mountains_count
  })

  return results



if __name__ == "__main__":
  # 표준 입력에서 JSON 데이터 수신 변경
  # stdin의 인코딩을 UTF-8로 설정
  input_stream = sys.stdin.buffer
  input_data = input_stream.read().decode('utf-8')

  bcontents = json.loads(input_data)
  print("Received bcontents for analysis:", bcontents)

  result = analyze_reviews(bcontents)

  # 결과를 파일로 저장
  save_path = 'd:/kdt/projects/hikers/src/main/resources/static/files/test.txt'
  os.makedirs(os.path.dirname(save_path), exist_ok=True)
  with open(save_path, 'w', encoding='utf-8') as f:
    for item in result:
      # UTF-8로 인코딩하여 파일에 쓰기
      f.write(json.dumps(item, ensure_ascii=False) + '\n')

  print("File saved at", save_path)
