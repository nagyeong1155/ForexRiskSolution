import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
from streamlit_autorefresh import st_autorefresh
from streamlit_extras.switch_page_button import switch_page # switch_page 임포트 확인

st.set_page_config(
    page_title="환율 뉴스", # 이 페이지의 page_title
    page_icon="📰"
)

# --- 공통: 페이지 순서 정의 (Streamlit이 인식하는 이름 기준) ---
# 메인 페이지는 'streamlit app'으로 변경했습니다.
PAGE_TITLES_ORDER = ["streamlit app", "환리스크 분석", "환율 뉴스"]

# --- 현재 날짜 및 시간 출력 ---
st.markdown(f"<p style='text-align: right; font-size: 0.9em; color: gray;'>현재 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}</p>", unsafe_allow_html=True)

st.title("📰 환율 뉴스 및 시장 심리")
st.write("선택한 날짜의 주요 환율 뉴스 기사와 시장 감성 분석 결과를 확인하세요.")

# --- 자동 새로고침 설정 (1시간마다 새로고침) ---
st_autorefresh(interval=3600 * 1000, key="news_autorefresh")

st.markdown("---")

# --- 1. 날짜 선택 위젯 ---
current_date_for_app = datetime(2025, 7, 17).date() # 현재 시간을 2025년 7월 17일로 가정

selected_date = st.date_input(
    "뉴스를 확인할 날짜를 선택해주세요.",
    value=current_date_for_app,
    max_value=current_date_for_app,
    help="선택한 날짜의 환율 관련 뉴스를 보여줍니다."
)

st.markdown("---")
st.subheader(f"{selected_date.strftime('%Y년 %m월 %d일')} 주요 환율 뉴스")

# --- 2. 뉴스 데이터 로딩 및 감성 분석 (가상) ---
# 캐시된 데이터도 1시간(3600초) 후에는 만료되도록 설정
@st.cache_data(ttl=3600) 
def get_news_and_sentiment(date_obj):
    """
    선택된 날짜에 해당하는 뉴스 기사와 감성 분석 결과를 반환하는 가상 함수.
    실제로는 뉴스 API 연동 및 감성 분석 모델 호출이 필요합니다.
    """
    news_articles = []
    
    # 2025년 7월 17일 뉴스 (현재 기준 오늘)
    if date_obj == datetime(2025, 7, 17).date():
        news_articles = [
            {"title": "원/달러 환율, 글로벌 달러 강세에 1360원 돌파", "link": "https://example.com/news_20250717_1", "sentiment": -0.6, "confidence": 0.90}, # 부정
            {"title": "한은, 금통위 개최…기준금리 동결 전망 우세", "link": "https://example.com/news_20250717_2", "sentiment": 0.0, "confidence": 0.70},   # 중립
            {"title": "미국 고용 지표 예상 상회, 연준 매파적 기조 유지 가능성", "link": "https://example.com/news_20250717_3", "sentiment": -0.7, "confidence": 0.92}  # 부정
        ]
    # 2025년 7월 16일 뉴스 (어제)
    elif date_obj == datetime(2025, 7, 16).date():
        news_articles = [
            {"title": "원/달러 환율 1350원대서 등락…FOMC 의사록 대기", "link": "https://example.com/news_20250716_1", "sentiment": 0.1, "confidence": 0.75}, 
            {"title": "코스피 상승세, 외국인 자금 유입 기대…원화 강세 압력", "link": "https://example.com/news_20250716_2", "sentiment": 0.6, "confidence": 0.88},
            {"title": "중국 경기 둔화 우려 지속, 아시아 환시 영향 촉각", "link": "https://example.com/news_20250716_3", "sentiment": -0.4, "confidence": 0.82}
        ]
    # 2025년 7월 15일 뉴스 (그제)
    elif date_obj == datetime(2025, 7, 15).date():
        news_articles = [
            {"title": "Fed, 추가 금리 인상 시사…글로벌 달러 강세 압력 확대", "link": "https://example.com/news_20250715_1", "sentiment": -0.7, "confidence": 0.95},
            {"title": "원화, 강달러에 밀려 연고점 경신…수출 기업 비상", "link": "https://example.com/news_20250715_2", "sentiment": -0.8, "confidence": 0.92},
            {"title": "국제 유가, 중동 불안에 배럴당 90달러 육박…인플레 우려", "link": "https://example.com/news_20250715_3", "sentiment": -0.5, "confidence": 0.80}
        ]
    # 다른 날짜는 뉴스가 없다고 가정
    else:
        news_articles = []

    avg_sentiment_score = 0.0
    avg_confidence_score = 0.0

    if news_articles:
        total_sentiment = sum(n['sentiment'] for n in news_articles)
        total_confidence = sum(n['confidence'] for n in news_articles)
        avg_sentiment_score = total_sentiment / len(news_articles)
        avg_confidence_score = total_confidence / len(news_articles)
    
    return news_articles, avg_sentiment_score, avg_confidence_score

news_list, avg_sentiment_score, avg_confidence_score = get_news_and_sentiment(selected_date)

if news_list:
    for news in news_list:
        st.markdown(f"#### [{news['title']}]({news['link']})")
        st.markdown(f"<p style='font-size:0.9em; color:gray;'>원문 링크</p>", unsafe_allow_html=True) 
        st.markdown("---")
else:
    st.info(f"선택하신 {selected_date.strftime('%Y년 %m월 %d일')}에는 환율 관련 뉴스가 없습니다.")

st.markdown("---")

st.subheader("📰 뉴스 감성 분석 결과")

if news_list:
    sentiment_label = ""
    sentiment_color = "black"
    impact_explanation = ""
    
    weighted_sentiment = avg_sentiment_score * avg_confidence_score 
    
    prob_decrease = (weighted_sentiment + 1) / 2 * 0.8 + 0.1 
    prob_increase = 1 - prob_decrease
    
    prob_decrease = round(prob_decrease * 100) / 100
    prob_increase = round(prob_increase * 100) / 100

    if prob_decrease > prob_increase + 0.05: 
        sentiment_label = "긍정적"
        sentiment_color = "blue"
        impact_explanation = "전반적인 뉴스 감성이 **긍정적**입니다. 이는 한국 경제에 대한 기대감 또는 달러 약세 요인이 부각될 때 나타날 수 있으며, **원화 강세 (환율 하락)** 압력으로 작용할 가능성이 높습니다."
    elif prob_increase > prob_decrease + 0.05: 
        sentiment_label = "부정적"
        sentiment_color = "red"
        impact_explanation = "전반적인 뉴스 감성이 **부정적**입니다. 이는 글로벌 경기 침체 우려, 국내 경제 불안, 또는 달러 강세 요인이 부각될 때 나타날 수 있으며, **원화 약세 (환율 상승)** 압력으로 작용할 가능성이 높습니다."
    else:
        sentiment_label = "중립적"
        sentiment_color = "grey"
        impact_explanation = "전반적인 뉴스 감성이 **중립적**입니다. 특정 방향으로의 강한 신호는 없으며, 시장은 다음 주요 지표 발표나 이벤트에 주목할 것으로 보입니다."
    
    st.markdown(f"**평균 감성 점수:** <span style='font-size:1.2em;'>**{avg_sentiment_score:.2f}**</span> (범위: -1.0 ~ 1.0, 1.0에 가까울수록 긍정적)", unsafe_allow_html=True)
    st.markdown(f"**감성 분석 신뢰도:** <span style='font-size:1.2em;'>**{avg_confidence_score:.2f}**</span> (범위: 0.0 ~ 1.0, 1.0에 가까울수록 신뢰도 높음)", unsafe_allow_html=True)
    st.markdown(f"**전반적인 뉴스 감성:** <span style='color:{sentiment_color}; font-size:1.2em;'>**{sentiment_label}**</span>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:0.9em; line-height:1.5;'>{impact_explanation}</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("환율 방향에 미칠 영향")
    st.markdown(f"뉴스 감성 분석 결과에 따르면, 현재 시장 심리는 다음과 같은 **환율 변동 가능성**을 시사합니다.")
    st.write(f"- **환율 상승 (원화 약세) 영향 확률:** **<span style='color: {'red' if prob_increase > prob_decrease else 'black'}'>{prob_increase * 100:.1f}%</span>**", unsafe_allow_html=True)
    st.write(f"- **환율 하락 (원화 강세) 영향 확률:** **<span style='color: {'blue' if prob_decrease > prob_increase else 'black'}'>{prob_decrease * 100:.1f}%</span>**", unsafe_allow_html=True)

else:
    st.info("뉴스가 없어 감성 분석을 진행할 수 없습니다.")

st.markdown("---")
st.info("💡 **면책 조항:** 감성 분석 결과는 AI 모델에 기반한 시장 심리 추정치이며, 실제 시장의 복잡한 요인을 100% 반영하지 않을 수 있습니다. 제시된 환율 영향 확률은 **감성 분석 결과만을 바탕으로 한 추정치**이며, 실제 환율 예측과는 다를 수 있습니다. 참고 자료로 활용해주세요. 투자 결정은 신중하게 내리셔야 합니다.")

st.markdown("---")

# --- 네비게이션 버튼 섹션 ---
current_page_title_for_nav = "환율 뉴스" # 이 페이지의 page_title
current_page_index = PAGE_TITLES_ORDER.index(current_page_title_for_nav)

nav_cols = st.columns(3)

with nav_cols[0]:
    if current_page_index > 0:
        if st.button("⬅️ 이전 페이지", use_container_width=True, key="news_prev_btn"):
            switch_page(PAGE_TITLES_ORDER[current_page_index - 1])
    else:
        st.button("⬅️ 이전 페이지", disabled=True, use_container_width=True, key="news_prev_disabled_btn")

with nav_cols[1]:
    if st.button("🏠 홈으로", use_container_width=True, key="news_home_btn"):
        switch_page("streamlit app") # 'streamlit app'으로 변경

with nav_cols[2]:
    if current_page_index < len(PAGE_TITLES_ORDER) - 1:
        if st.button("➡️ 다음 페이지", use_container_width=True, key="news_next_btn"):
            switch_page(PAGE_TITLES_ORDER[current_page_index + 1])
    else:
        st.button("➡️ 다음 페이지", disabled=True, use_container_width=True, key="news_next_disabled_btn")

st.markdown("---")

