import streamlit as st
import pandas as pd
from datetime import date, timedelta
import random

# 현재 날짜 기준
today = date.today()

# --- 1. 예측 모델 및 관련 함수 (가상 - 확률 기반 & 예측 환율 포함) ---
def exchange_rate_probability_model(transaction_completion_date, current_krw_usd_rate):
    """
    거래 완료 시점에 대한 환율 변동 확률과 각 시나리오별 예상 환율을 반환하는 가상 함수.
    """
    days_diff = (transaction_completion_date - today).days

    # 시나리오별 확률 및 예상 환율 (가상)
    probabilities = {}
    predicted_rates = {} # 각 시나리오별 예상 환율
    
    # 임의의 변동폭 (예: 하락 시 2-5%, 상승 시 2-5%, 보합 시 -0.5% ~ 0.5%)
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
            "상승": upper_bound_increase,
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
    # 이 함수는 이전과 동일하게 사용
    if transaction_type == "수출":
        if dominant_trend == "하락":
            return "선물환 매도 (환율 하락 위험 헷지)"
        elif dominant_trend == "상승":
            return "현물환 보유 후 환율 상승 시 매도 (상승 이익 추구)"
        else: # 보합 예상
            return "상황 주시 및 유동적 대응"
    elif transaction_type == "수입":
        if dominant_trend == "상승":
            return "선물환 매수 (환율 상승 위험 헷지)"
        elif dominant_trend == "하락":
            return "현물환 매수 후 환율 하락 시 재매수 고려 (하락 이익 추구)"
        else: # 보합 예상
            return "상황 주시 및 유동적 대응"
    return "전략 없음"

# --- 2. Streamlit UI 구성 ---

st.set_page_config(layout="centered", page_title="기업 맞춤형 환리스크 솔루션")

st.title("💰 기업 맞춤형 환리스크 솔루션")
st.markdown("---")

st.subheader("📊 현재 환율 정보 (USD/KRW)")
current_krw_usd_rate = 1353 # 현재 환율 (가상)

col1, col2, col3, col4 = st.columns(4)
col1.metric("현재 환율", f"₩{current_krw_usd_rate:,.0f}")
col2.metric("전일 대비", "+8", "상승")
col3.metric("오늘 고점", "1,396")
col4.metric("오늘 저점", "1,350")
st.markdown("---")

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

if submit_button:
    st.markdown("---")
    st.subheader("📈 환리스크 분석 결과")

    # 예측 확률 및 예상 환율 계산
    prediction_data = exchange_rate_probability_model(transaction_completion_date, current_krw_usd_rate)
    
    # 주요 추세, 리스크 라벨, 그리고 해당 추세의 대표 예상 환율 가져오기
    risk_label_text, dominant_trend, dominant_predicted_rate = get_risk_label_and_dominant_trend(prediction_data)

    # 전략 추천
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
    st.subheader("📊 시나리오별 예상 효과 (KRW 환산)")
    st.write(f"현재 USD {amount:,.0f} 상당의 금액은 ₩{(amount * current_krw_usd_rate):,.0f} 입니다.")

    simulated_data = {
        '시나리오': [],
        '확률 (%)': [],
        '예상 환율 (USD/KRW)': [],
        '예상 원화 금액 (KRW)': [],
        '현재 대비 변동 (KRW)': []
    }

    # 확률이 높은 순서대로 시나리오를 표시
    sorted_scenarios = sorted(prediction_data["probabilities"].items(), key=lambda item: item[1], reverse=True)

    for scenario_name, prob in sorted_scenarios:
        simulated_data['시나리오'].append(scenario_name)
        simulated_data['확률 (%)'].append(f"{prob*100:.1f}")
        
        # 가상 환율 적용
        expected_rate = prediction_data["predicted_rates"][scenario_name]
        
        simulated_data['예상 환율 (USD/KRW)'].append(expected_rate)
        expected_krw_amount = expected_rate * amount
        simulated_data['예상 원화 금액 (KRW)'].append(expected_krw_amount)
        
        # 현재 환율 기준과 비교
        current_krw_amount = current_krw_usd_rate * amount
        diff = expected_krw_amount - current_krw_amount
        simulated_data['현재 대비 변동 (KRW)'].append(f"{diff:,.0f}" if diff >= 0 else f"-{abs(diff):,.0f}") # 음수 표기 명확히

    df_sim = pd.DataFrame(simulated_data)
    
    # 데이터프레임 형식 변경 (환율과 금액은 소수점 없는 정수로)
    df_sim['예상 환율 (USD/KRW)'] = df_sim['예상 환율 (USD/KRW)'].apply(lambda x: f"{x:,.0f}")
    df_sim['예상 원화 금액 (KRW)'] = df_sim['예상 원화 금액 (KRW)'].apply(lambda x: f"{x:,.0f}")

    st.table(df_sim.set_index('시나리오'))

    st.markdown("---")
    st.info("💡 **면책 조항:** 이 솔루션은 과거 데이터 및 통계적 모델에 기반한 확률적 예측이며, 실제 시장 상황과 다를 수 있습니다. 제시된 정보는 참고용이며, 투자 결정은 항상 신중하게 내리셔야 합니다. 은행은 본 정보로 인한 직간접적인 손실에 대해 책임을 지지 않습니다.")