import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from datetime import datetime

st.set_page_config(
    page_title="환리스크 솔루션", # 이 페이지의 page_title
    page_icon="💰",
    layout="centered"
)

# --- 공통: 페이지 순서 정의 (page_title 기준) ---
# 이 순서는 pages 폴더의 파일명과 각 페이지의 st.set_page_config(page_title=...)에 따라 정확히 맞춰주세요.
PAGE_TITLES_ORDER = ["환리스크 솔루션", "환리스크 분석", "환율 뉴스"]

# --- 현재 날짜 및 시간 출력 ---
st.markdown(f"<p style='text-align: right; font-size: 0.9em; color: gray;'>현재 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}</p>", unsafe_allow_html=True)

st.title("🏡 홈페이지")
st.write("환리스크 솔루션에 오신 것을 환영합니다!")
st.write("아래 버튼을 클릭하여 각 기능을 이용해주세요.")

st.markdown("""
### 주요 기능:
- **환리스크 분석**: 기업의 거래 정보를 바탕으로 환율 변동 확률과 추천 전략을 제공합니다.
- **환율 뉴스**: 주요 경제 지표 및 환율 관련 최신 뉴스를 확인합니다.
""")

col1, col2 = st.columns(2)

with col1:
    if st.button("📈 환리스크 분석 시작하기", use_container_width=True, key="home_to_analysis_btn"):
        switch_page("환리스크 분석") # pages/1_환리스크_분석.py의 page_title

with col2:
    if st.button("📰 환율 뉴스 확인하기", use_container_width=True, key="home_to_news_btn"):
        switch_page("환율 뉴스") # pages/2_환율_뉴스.py의 page_title



st.info("💡 **면책 조항:** 이 솔루션은 과거 데이터 및 통계적 모델에 기반한 확률적 예측이며, 실제 시장 상황과 다를 수 있습니다. 제시된 정보는 참고용이며, 투자 결정은 항상 신중하게 내리셔야 합니다. 은행은 본 정보로 인한 직간접적인 손실에 대해 책임을 지지 않습니다.")
st.markdown("---")

# --- 네비게이션 버튼 섹션 ---
current_page_title = "환리스크 솔루션" # 현재 페이지의 page_title
current_page_index = PAGE_TITLES_ORDER.index(current_page_title)

nav_cols = st.columns(3)

# 이전 페이지 버튼
with nav_cols[0]:
    if current_page_index > 0:
        if st.button("⬅️ 이전 페이지", use_container_width=True, key="home_prev_btn"):
            switch_page(PAGE_TITLES_ORDER[current_page_index - 1])
    else:
        st.button("⬅️ 이전 페이지", disabled=True, use_container_width=True, key="home_prev_disabled_btn") # 첫 페이지일 때 비활성화



# 다음 페이지 버튼
with nav_cols[2]:
    if current_page_index < len(PAGE_TITLES_ORDER) - 1:
        if st.button("➡️ 다음 페이지", use_container_width=True, key="home_next_btn"):
            switch_page(PAGE_TITLES_ORDER[current_page_index + 1])
    else:
        st.button("➡️ 다음 페이지", disabled=True, use_container_width=True, key="home_next_disabled_btn") # 마지막 페이지일 때 비활성화

st.markdown("---")
