import streamlit as st
from datetime import datetime
import requests
import re
from collections import Counter

# 📅 현재 시간 출력
now = datetime.now()
st.markdown(f"🕒 {now.strftime('%Y.%m.%d %H:%M')} 업데이트 (최근 24시간 수집)")
st.markdown("## 💬 환율 뉴스 키워드 TOP 10")

# 📡 네이버 뉴스 API로 데이터 수집
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

# 🧠 간단한 단어 추출 (형태소 분석 없이)
def extract_keywords(text):
    words = re.findall(r'\b[가-힣]{2,}\b', text)  # 한글 2자 이상 단어만
    words = [word for word in words if word not in ['있습니다', '합니다', '관련']]  # 불용어 제거 예시
    counter = Counter(words)
    return counter.most_common(10)

# 🔁 새로고침 버튼
if st.button("🔄 새로고침"):
    st.rerun()

# 실행
try:
    text = get_news_text("환율")
    keywords = extract_keywords(text)

    for i, (word, count) in enumerate(keywords, 1):
        st.markdown(f"{i}. **{word}** ({count}회)")

except Exception as e:
    st.error("뉴스 키워드 수집에 실패했습니다.")
    st.exception(e)
