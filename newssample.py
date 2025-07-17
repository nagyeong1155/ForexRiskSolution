# sample.py

import streamlit as st
from datetime import datetime
import requests
from collections import Counter
from konlpy.tag import Okt
import re

# 1. 현재 시간 표시
now = datetime.now()
st.markdown(f"🕒 {now.strftime('%Y.%m.%d %H:%M')} 업데이트 (최근 24시간 수집)")
st.markdown("## 💬 환율 뉴스 키워드 TOP 10")

# 2. 뉴스 수집 함수 (네이버 뉴스 OpenAPI 활용)
def get_news_text(query="환율", display=50):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&sort=date"
    headers = {
        "X-Naver-Client-Id": "D4sfyB2MAnV3cgZJJfD_",
        "X-Naver-Client-Secret": "2KNukij4FX"
    }
    res = requests.get(url, headers=headers).json()
    items = res.get("items", [])
    text = " ".join([item["title"] + " " + item["description"] for item in items])
    return text

# 3. 키워드 추출
def extract_keywords(text):
    okt = Okt()
    words = okt.nouns(re.sub(r"[^가-힣 ]", "", text))  # 한글만 추출
    words = [w for w in words if len(w) > 1]  # 한 글자 제거
    freq = Counter(words)
    return freq.most_common(10)

# 4. 전체 실행
try:
    text = get_news_text("환율")
    keywords = extract_keywords(text)

    for i, (word, count) in enumerate(keywords, 1):
        st.markdown(f"{i}. **{word}** ({count}회)")

except Exception as e:
    st.error("키워드 추출에 실패했습니다.")
    st.exception(e)

if st.button("🔄 새로고침"):
    st.rerun()

