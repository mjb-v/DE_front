# 자재계획관리

from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime

font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

# FastAPI URL
API_URL = "http://127.0.0.1:8000"

# 한글 컬럼명으로 변환
def translate_data(data):
    translation_dict = {
        "year": "년도",
        "month": "월",
        "business_plan": "사업계획",
        "business_amount": "실적",
        "business_achievement_rate": "사업달성율",
        "item_number": "품번",
        "item_name": "품명",
        "client_code": "거래처코드",
        "previous_amount": "전월실적",
        "current_amount": "당월실적",
        "growth_rate": "증감율",
        "client": "거래처명", # (dropdown: (주)금성오토텍, 
        "model": "모델구분", # (dropdown: 가정, 건조기, 세탁기, 식기세척기, 에어컨, 중장비)
        "item_category": "품목구분", # (dropdown: 원재료, 부재료, 재공품, 제품, 반제품)
        "process": "공정구분", # (drodown: 검사/조립, 사출)
        "quantity": "계획수량"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

# 임시 주소 사용
def get_material_all_plan(year: int):
    url = f"{API_URL}/material_plans/{year}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

# ----------------------------------------------------------------

st.title("자재 계획 관리")
tab = st.sidebar.selectbox("", ["자재 계획 관리", "자재 계획 등록"])

if tab == "자재 계획 관리":
    st.subheader("자재 계획")
    selected_year = st.selectbox("년도 선택", list(range(2014, 2025)))
    material_plan_data = get_material_all_plan(selected_year)

    if material_plan_data:
        df = pd.DataFrame(material_plan_data)
        df = translate_data(df)
        df = df.drop(columns=["년도"])

        # 테이블 형식으로 변환 (month를 columns로, 나머지를 index로 변환)
        df_pivot = df.set_index('월').T
        df_pivot.columns = [f"{month}월" for month in df_pivot.columns]  # month를 '월'로 변환

        # 테이블 출력
        st.subheader(f"{selected_year}년도 계획 및 실적 데이터")
        st.dataframe(df_pivot)

        # 그래프
        st.subheader(f"{selected_year}년 차트")

        # 월별로 사업 달성률과 생산 달성률 데이터 추출
        business_achievement_rates = df["사업달성율"]
        months = df["월"].apply(lambda x: f"{x}월")

        fig, ax = plt.subplots(figsize=(8, 6))

        # 막대그래프에 월별 데이터 추가
        ax.bar(months, business_achievement_rates, width=0.4, label='사업 달성률', align='center', color='#ff9999')

        # 그래프에 텍스트와 제목 추가
        ax.set_ylim(0, 100)  # y축 범위 0~100
        ax.set_ylabel('달성률 (%)')
        ax.set_title(f"{selected_year}년 월별 사업 달성률")
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("계획 데이터가 없습니다.")







