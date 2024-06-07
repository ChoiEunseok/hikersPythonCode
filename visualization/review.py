import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import numpy as np
import seaborn as sns
import io
import base64
from sqlalchemy import create_engine

# 연결 문자열 설정
connection_string = 'oracle+cx_oracle://c##mountain:mountain1234@192.168.0.29/?service_name=xe'
engine = create_engine(connection_string)
connection = engine.connect()

# 쿼리 실행 및 결과를 DataFrame으로 변환
query = """
select mt.mntn_code, mt.mntn_nm, 
mt.mntn_loc, mt.city, bb.title, bb.bcontent, 
bb.staring, bb.ctime, bb.cdate, bb.tags
FROM bbs bb
    LEFT JOIN mountain mt
    ON mt.mntn_code = bb.mntn_code
where bb.status != 'D' and bb.status !='W'
    """
df = pd.read_sql_query(query, connection)
connection.close()

df = df.rename(columns={
    'mntn_code': '산코드',
    'mntn_nm': '산이름',
    'mntn_loc': '산주소',
    'city': '시도명',
    'title': '글제목',
    'bcontent': '글내용',
    'staring': '별점',
    'ctime': '등반시간',
    'cdate': '작성일',
    'tags': '태그'
})
df['산코드'] = df['산코드'].astype('object')  # 산코드 열의 데이터 유형을 object로 변환
df['산코드'] = df['산코드'].astype(str).str.split('.').str[0]  # 문자열로 변환하여 소수점 이하 제거

def create_plot():
    plots = []

    # 리뷰 wordcloud

    from konlpy.tag import Okt
    from wordcloud import WordCloud

    okt = Okt()
    font_path = r'c:\windows\Fonts\malgun.ttf'

    contents = " ".join(df['글내용'])
    nouns = okt.nouns(contents)
    joined_contents = ' '.join(nouns)
    joined_contents

    def display_word_cloud(data, /, *, width=1200, height=500, stopwords=[], mask=None, title=''):
        wordcloud = WordCloud(
            font_path=font_path,
            width=width,
            height=height,
            random_state=2024,
            background_color='white',
            stopwords=stopwords,  # 불용어 제거
            mask=mask
        ).generate(data)
        plt.figure()
        plt.title(title)
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        return wordcloud

    stopwords = ['테스트', 'test', '신고', '등', '산', '오늘', '수', '것', '정말', '모든', '동안']

    contents = " ".join(df['글내용'])
    display_word_cloud(joined_contents, width=2000, height=1000, stopwords=stopwords, title='사용자 wordcloud')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots.append(base64.b64encode(buf.read()).decode('utf-8'))
    plt.close()

    # 첫 번째 차트: 산별 리뷰 개수(막대)
    # 산 이름별 리뷰 개수 계산
    review_counts = df['산이름'].value_counts().reset_index()
    review_counts.columns = ['산이름', 'count']
    top_n = 10
    top_review_counts = review_counts.head(top_n)
    plt.figure(figsize=(10, 6))
    top_review_counts.set_index('산이름')['count'].plot(kind='bar')
    plt.title(f'산별 리뷰 개수(상위 {top_n}개)')
    plt.xlabel('산 이름')
    plt.ylabel('리뷰 개수')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots.append(base64.b64encode(buf.read()).decode('utf-8'))
    plt.close()

    # 두 번째 차트: 상위 10개의 산별 리뷰 비율(파이차트)
    pie_chart_width = 8
    pie_chart_height = 8
    plt.figure(figsize=(pie_chart_width, pie_chart_height))
    df['시도명'].value_counts().head(10).plot(kind='pie', autopct='%1.1f%%', startangle=140)
    plt.title('방문 산의 시도명별 비율')
    plt.ylabel(None)  # y축 라벨 제거
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots.append(base64.b64encode(buf.read()).decode('utf-8'))
    plt.close()

    # 세 번째 차트: 상위 10개의 산별 평균 별점
    # 산 이름별 평균 별점 계산
    avg_star_ratings = df.groupby(['산이름'])['별점'].mean().reset_index()
    avg_star_ratings.columns = ['산이름', '평균 별점']
    top_n = 10
    top_avg_star_ratings = avg_star_ratings.nlargest(top_n, '평균 별점')
    plt.figure(figsize=(10, 6))
    plt.bar(top_avg_star_ratings['산이름'], top_avg_star_ratings['평균 별점'], color='skyblue')
    plt.title(f'산별 평균 별점(상위 {top_n}개)')
    plt.xlabel('산 이름')
    plt.ylabel('평균 별점')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots.append(base64.b64encode(buf.read()).decode('utf-8'))
    plt.close()

    # 네 번째 차트: 일자별 게시글 업로드 추이
    df['작성일'] = pd.to_datetime(df['작성일'])
    daily_post_counts = df.groupby(df['작성일'].dt.date).size()
    plt.figure(figsize=(10, 5))
    daily_post_counts.plot(kind='line', marker='o', color='skyblue')
    plt.title('일자별 게시글 업로드 추이')
    plt.xlabel('날짜')
    plt.xticks(rotation=30)
    plt.ylabel('게시글 수')
    plt.grid(True)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots.append(base64.b64encode(buf.read()).decode('utf-8'))
    plt.close()
    
    return plots


if __name__ == "__main__":
    plots = create_plot()
    for plot in plots:
        print(plot)
        print("---END---")
