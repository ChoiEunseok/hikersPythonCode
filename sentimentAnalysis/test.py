import sys
import json

def process_data(data):
    results = []  # 결과를 저장할 리스트
    for review in data:
        review_length = len(review)
        if review_length >= 50:
            positive_rate = 1.0  # 긍정적인 리뷰로 간주
            negative_rate = 0.0
        else:
            positive_rate = 0.0
            negative_rate = 1.0  # 부정적인 리뷰로 간주

        # 결과 리스트에 추가
        results.append({
            'review': review,
            'positive_rate': positive_rate,
            'negative_rate': negative_rate
        })
    print("Received results for analysis:", results)
    return results

if __name__ == "__main__":
    # 표준 입력에서 JSON 데이터 수신
    input_data = sys.stdin.read()
    bcontents = json.loads(input_data)

    print("Received bcontents for analysis:", bcontents)

    # 데이터 처리
    result = process_data(bcontents)

    # 처리 결과를 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False))

