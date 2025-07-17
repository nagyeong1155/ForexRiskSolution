import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
from streamlit_extras.switch_page_button import switch_page
# from streamlit_autorefresh import st_autorefresh # 자동 새로고침 기능 제거를 위해 이 줄 주석 처리 또는 삭제

st.set_page_config(
    page_title="환리스크 분석", # 이 페이지의 page_title
    page_icon="📈",
    layout="wide" # 넓은 레이아웃을 사용하여 3단 컬럼이 잘 보이도록 설정
)

# --- 공통: 페이지 순서 정의 (Streamlit이 인식하는 이름 기준) ---
PAGE_TITLES_ORDER = ["streamlit app", "환리스크 분석", "환율 뉴스"]

# --- 현재 날짜 및 시간 출력 ---
st.markdown(f"<p style='text-align: right; font-size: 0.9em; color: gray;'>현재 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}</p>", unsafe_allow_html=True)

# --- 자동 새로고침 설정 (예: 10초마다 시간 업데이트용) ---
# st_autorefresh(interval=10 * 1000, key="risk_analysis_time_refresh") # 자동 새로고침 기능 제거를 위해 이 줄 주석 처리 또는 삭제


st.title("📈 기업 맞춤형 환리스크 분석")
st.write("기업의 거래 정보를 입력하여 환율 변동 확률과 추천 전략을 확인하세요.")

st.markdown("---")

# --- 1. 예측 모델 및 관련 함수 (가상 - 확률 기반 & 예측 환율 포함) ---
today = datetime.now().date() 

def exchange_rate_probability_model(transaction_completion_date, current_krw_usd_rate):
    """
    거래 완료 시점에 대한 환율 변동 확률과 각 시나리오별 예상 환율을 반환하는 가상 함수.
    """
    days_diff = (transaction_completion_date - today).days

    probabilities = {}
    predicted_rates = {} 
    
    lower_bound_decrease = current_krw_usd_rate * (1 - random.uniform(0.02, 0.05))
    upper_bound_increase = current_krw_usd_rate * (1 + random.uniform(0.02, 0.05))
    stable_rate = current_krw_usd_rate * (1 + random.uniform(-0.005, 0.005))

    if days_diff <= 0:
        probabilities = {"하락": 0.0, "상승": 0.0, "보합": 1.0}
        predicted_rates = {"하락": current_krw_usd_rate, "상승": current_krw_usd_rate, "보합": current_krw_usd_rate}
    elif days_diff <= 30: # 1개월 이내
        probabilities = {"하락": 0.40, "상승": 0.50, "보합": 0.10}
        predicted_rates = {
            "하락": lower_bound_decrease,
            "상승": upper_bound_increase,
            "보합": stable_rate
        }
    elif days_diff <= 90: # 1개월 ~ 3개월
        probabilities = {"하락": 0.55, "상승": 0.35, "보합": 0.10}
        predicted_rates = {
            "하락": lower_bound_decrease,
            "상승": upper_bound_increase,
            "보합": stable_rate
        }
    else: # 3개월 이상
        probabilities = {"하락": 0.65, "상승": 0.25, "보합": 0.10}
        predicted_rates = {
            "하락": lower_bound_decrease,
            "상승": upper_bound_increase, # <-- '상ง' 오타 수정 완료
            "보합": stable_rate
        }
    
    return {"probabilities": probabilities, "predicted_rates": predicted_rates}


def get_risk_label_and_dominant_trend(data):
    """
    확률을 기반으로 주요 추세, 리스크 라벨, 그리고 해당 추세의 대표 예상 환율을 반환합니다.
    """
    probabilities = data["probabilities"]
    predicted_rates = data["predicted_rates"]

    max_prob_key = max(probabilities, key=probabilities.get)
    max_prob_value = probabilities[max_prob_key]
    
    dominant_predicted_rate = predicted_rates[max_prob_key] # 주요 추세의 예상 환율

    if max_prob_key == "하락":
        return "환율 하락 예상 (확률 {:.1f}%)".format(max_prob_value * 100), "하락", dominant_predicted_rate
    elif max_prob_key == "상승":
        return "환율 상승 예상 (확률 {:.1f}%)".format(max_prob_value * 100), "상승", dominant_predicted_rate
    else:
        return "환율 보합 예상 (확률 {:.1f}%)".format(max_prob_value * 100), "보합", dominant_predicted_rate

def get_strategy_recommendation_prob(dominant_trend, transaction_type):
    if transaction_type == "수출":
        if dominant_trend == "하락":
            return "선물환 매도 (환율 하락 위험 헷지)"
        elif dominant_trend == "상승":
            return "현물환 보유 후 환율 상승 시 매도 (상승 이익 추구)"
        else:
            return "상황 주시 및 유동적 대응"
    elif transaction_type == "수입":
        if dominant_trend == "상승":
            return "선물환 매수 (환율 상승 위험 헷지)"
        elif dominant_trend == "하락":
            return "현물환 매수 후 환율 하락 시 재매수 고려 (하락 이익 추구)"
        else:
            return "상황 주시 및 유동적 대응"
    return "전략 없음"

# --- 2. Streamlit UI 구성 ---

# 3단 컬럼 생성
col_current_rate, col_transaction_input, col_analysis_result = st.columns(3)

# --- [0] 현재 환율 정보 (USD/KRW) ---
with col_current_rate:
    st.subheader("📊 현재 환율 정보 (USD/KRW)")
    current_krw_usd_rate = 1353 

    col1, col2 = st.columns(2) # 내부적으로 2단 컬럼
    with col1:
        st.metric("현재 환율", f"₩{current_krw_usd_rate:,.0f}")
        st.metric("오늘 고점", "1,396")
    with col2:
        st.metric("전일 대비", "+8", "상승")
        st.metric("오늘 저점", "1,350")
    st.markdown("---")


# --- [1] 거래 정보 입력 (통화: USD) ---
with col_transaction_input:
    st.subheader("📝 거래 정보 입력 (통화: USD)")

    with st.form("transaction_form"):
        transaction_type = st.radio("거래 유형", ("수출", "수입"), help="기업의 거래 유형을 선택해주세요.")
        
        st.markdown("**거래 통화: USD** (환율 예측 모델이 USD/KRW에 특화되어 있습니다.)")
        
        amount = st.number_input("거래 금액 (USD)", min_value=1000, value=1000000, step=1000, help="거래 금액을 USD 단위로 입력해주세요.")
        
        transaction_start_date = st.date_input("거래 시작일", value=today, help="거래가 시작되는 날짜를 선택해주세요.")
        transaction_completion_date = st.date_input("거래 완료일 (예측 시점)", value=today + timedelta(days=90), 
                                                    min_value=today + timedelta(days=1),
                                                    help="미래에 외화 결제가 완료될 것으로 예상되는 날짜를 선택해주세요. 이 날짜 기준으로 환율을 예측합니다.")

        submit_button = st.form_submit_button("환리스크 분석")


# --- [2] 환리스크 분석 결과 (버튼 클릭 시만 표시) ---
with col_analysis_result:
    if submit_button: # submit_button이 True일 때만 이 섹션이 렌더링됨
        st.subheader("📈 환리스크 분석 결과")

        prediction_data = exchange_rate_probability_model(transaction_completion_date, current_krw_usd_rate)
        
        risk_label_text, dominant_trend, dominant_predicted_rate = get_risk_label_and_dominant_trend(prediction_data)

        recommended_strategy = get_strategy_recommendation_prob(dominant_trend, transaction_type)

        st.write(f"**거래 유형:** {transaction_type}")
        st.write(f"**거래 통화:** USD")
        st.write(f"**거래 금액:** ${amount:,.0f}")
        st.write(f"**거래 시작일:** {transaction_start_date.strftime('%Y년 %m월 %d일')}")
        st.write(f"**거래 완료일 (예측 시점):** {transaction_completion_date.strftime('%Y년 %m월 %d일')}")
        st.markdown(f"**현재 USD/KRW 환율:** ₩{current_krw_usd_rate:,.0f}")

        st.markdown("---")
        st.subheader("📊 환율 변동 확률 ({})".format(transaction_completion_date.strftime('%Y년 %m월 %d일') + " 기준"))
        
        probabilities = prediction_data["probabilities"]
        
        st.write(f"- **하락할 확률:** <span style='color: {'red' if dominant_trend == '하락' else 'black'}'>{probabilities['하락'] * 100:.1f}%</span>", unsafe_allow_html=True)
        st.write(f"- **상승할 확률:** <span style='color: {'blue' if dominant_trend == '상승' else 'black'}'>{probabilities['상승'] * 100:.1f}%</span>", unsafe_allow_html=True)
        st.write(f"- **보합할 확률:** <span style='color: {'black' if dominant_trend == '보합' else 'black'}'>{probabilities['보합'] * 100:.1f}%</span>", unsafe_allow_html=True)
        
        st.markdown(f"**➡ 주요 예상:** <span style='color: {'red' if dominant_trend == '하락' else ('blue' if dominant_trend == '상승' else 'black')}'>{risk_label_text}</span>", unsafe_allow_html=True)
        st.markdown(f"**➡ 예상 환율 ({dominant_trend} 시):** ₩<span style='color: {'red' if dominant_trend == '하락' else ('blue' if dominant_trend == '상승' else 'black')}'>{dominant_predicted_rate:,.0f}</span>", unsafe_allow_html=True)


        st.markdown("---")
        st.subheader("💡 추천 전략")
        if "선물환 매도" in recommended_strategy:
            st.success(f"**{recommended_strategy}**")
            st.info(f"주요 예상은 **환율 하락**입니다. {transaction_type} 기업의 경우, 미래에 받을 USD 금액의 원화 가치 하락 위험을 헷지하기 위해 **선물환 매도**를 고려하는 것이 유리합니다.")
        elif "선물환 매수" in recommended_strategy:
            st.warning(f"**{recommended_strategy}**")
            st.info(f"주요 예상은 **환율 상승**입니다. {transaction_type} 기업의 경우, 미래에 지급할 USD 금액의 원화 부담 증가 위험을 헷지하기 위해 **선물환 매수**를 고려하는 것이 유리합니다.")
        else:
            st.info(f"**{recommended_strategy}**")
            st.info("주요 예상은 **환율 보합**입니다. 시장 상황을 면밀히 주시하며 유동적으로 대응하는 것을 추천합니다.")

        st.markdown("---")
        
st.markdown("---")

# --- 네비게이션 버튼 섹션 (컬럼 외부) ---
current_page_title_for_nav = "환리스크 분석" # 현재 페이지의 page_title
current_page_index = PAGE_TITLES_ORDER.index(current_page_title_for_nav)

nav_cols = st.columns(3)

with nav_cols[0]:
    if current_page_index > 0:
        if st.button("⬅️ 이전 페이지", use_container_width=True, key="analysis_prev_btn"):
            switch_page(PAGE_TITLES_ORDER[current_page_index - 1])
    else:
        st.button("⬅️ 이전 페이지", disabled=True, use_container_width=True, key="analysis_prev_disabled_btn")

with nav_cols[1]:
    if st.button("🏠 홈으로", use_container_width=True, key="analysis_home_btn"):
        switch_page("streamlit app") 

with nav_cols[2]:
    if current_page_index < len(PAGE_TITLES_ORDER) - 1:
        if st.button("➡️ 다음 페이지", use_container_width=True, key="analysis_next_btn"):
            switch_page(PAGE_TITLES_ORDER[current_page_index + 1])
    else:
        st.button("➡️ 다음 페이지", disabled=True, use_container_width=True, key="analysis_next_disabled_btn")

st.markdown("---")

# --- 수동 새로고침 버튼 (옵션) ---
if st.button("🔄 페이지 새로고침 (수동)", use_container_width=True, key="analysis_refresh_btn"):
    st.rerun()