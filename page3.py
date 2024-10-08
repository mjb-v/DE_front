# 생산관리 3. 생산현황관리

from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

# FastAPI URL
load_dotenv()
API_URL = os.getenv("API_URL")

# 한글 컬럼명으로 변환
def translate_data(data):
    translation_dict = {
        "month": "월",
        "date": "가동일자",
        "process": "공정",
        "line": "라인",
        "operator": "작업자",
        "shift": "근무조",
        "model": "모델",
        "item_number": "품번",
        "item_name": "품명",
        "specification": "규격",
        "operating_time": "가동시간",
        "non_operating_time": "비가동시간",
        "target_quantity": "목표수량",
        "produced_quantity": "생산수량", # 여기까지 실시간 가동현황
        "production_efficiency": "생산효율", # 라인별 생산 효율 (생산수/목표수 * 100)
        "line_efficiency": "라인가동율", # 라인별 가동시간 대비 생산량 (생산수/가동시간)
        # 라인비가동율(비가동 시간이 많은 라인): 가동시간 / (가동시간 + 비가동시간) * 100
        "monthly_production_efficiency": "월별생산효율",
        "monthly_line_efficiency": "월별라인가동율"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

# 1. GET 실시간 가동 현황 데이터
def get_real_time_status(date=None):
    # 실시간을 위해 오늘 날짜로 설정
    if date is None:
        date = datetime.today().strftime('%Y-%m-%d')
    else:
        date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')

    response = requests.get(f"{API_URL}/productions/day/{date}")
    if response.status_code == 200:
        data = response.json()
        return translate_data(data)
    else:
        st.error("실시간 가동 현황 데이터를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

# 2. GET 연도별 효율 현황 데이터
def get_efficiency_status(year=2024):
    response = requests.get(f"{API_URL}/productions/efficiency/{year}")
    if response.status_code == 200:
        data = response.json()
        return translate_data(data)
    else:
        st.error("효율 현황 데이터를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

# '라인'별 '생산효율'과 '라인가동율'의 평균 계산
def calculate_average_by_line(df):
    df_grouped = df.groupby('라인', observed=False).agg({
        '생산효율': 'mean',
        '라인가동율': 'mean'
    }).reset_index()
    return df_grouped

# 1. 실시간 그래프
def plot1(df):
    df_grouped = calculate_average_by_line(df)
    df_grouped['라인'] = pd.Categorical(df_grouped['라인'], categories=[f"Line{i}" for i in range(1, 11)], ordered=True)
    df_grouped = df_grouped.sort_values('라인')

    fig, ax = plt.subplots(figsize=(10, 6))

    lines = df_grouped['라인']
    bar_width = 0.35
    index = np.arange(len(lines))

    ax.clear()
    
    bar1 = ax.bar(index, df_grouped['생산효율'], bar_width, label='생산효율', color='b', alpha=0.6)
    bar2 = ax.bar(index + bar_width, df_grouped['라인가동율'], bar_width, label='라인가동율', color='r', alpha=0.6)

    ax.set_xlabel('라인', fontsize=12)
    ax.set_ylabel('퍼센트 (%)', fontsize=12)
    ax.set_title('라인별 평균 생산효율과 라인가동율 (실시간)', fontsize=14)
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(lines, rotation=45)

    ax.legend()
    return fig

# 2. 전체 현황 그래프
def plot2(df, selected_year):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    months = df['월']
    bar_width = 0.35
    index = np.arange(len(months))

    bar1 = ax.bar(index, df['생산효율'], bar_width, label='생산효율', color='b', alpha=0.6)
    bar2 = ax.bar(index + bar_width, df['라인가동율'], bar_width, label='라인가동율', color='r', alpha=0.6)

    ax.set_xlabel('월', fontsize=12)
    ax.set_ylabel('퍼센트 (%)', fontsize=12)
    ax.set_title(f'{selected_year}년 생산효율과 라인가동율', fontsize=14)
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(months, rotation=45)

    ax.legend()
    st.pyplot(fig)
# ----------------------------------------------------------------

def page3_view():
    st.title("생산 현황 관리")
    tab = st.sidebar.radio("", ["실시간 가동 현황", "연도별 효율 현황"])

    if tab == "실시간 가동 현황":
        st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>필터 설정</div>", unsafe_allow_html=True)

        # Placeholder 생성
        table_placeholder = st.empty()
        chart_placeholder = st.empty()

        while True:
            df1 = get_real_time_status().drop(columns=['id', 'account_idx'])[
                ["가동일자", "공정", "라인", "작업자", "근무조", "품번", "품명", "규격", "가동시간", "생산수량", "생산효율", "라인가동율"]
            ]
            df1['라인'] = pd.Categorical(df1['라인'], categories=[f"Line{i}" for i in range(1, 11)], ordered=True)
            table_placeholder.dataframe(df1)
            with chart_placeholder:
                fig = plot1(df1)
                st.pyplot(fig)

            # 5초 대기 후 다시 업데이트
            time.sleep(5)

    elif tab == "연도별 효율 현황":
        st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>필터 설정</div>", unsafe_allow_html=True)
        selected_year = st.sidebar.selectbox("년도 선택", list(range(2014, 2025)), index=10)
        df2 = get_efficiency_status(selected_year).drop(columns=["year"])
        df2_pivot = df2.set_index('월').T
        df2_pivot.columns = [f"{month}월" for month in df2_pivot.columns]
        st.dataframe(df2_pivot.style.set_properties(**{'width': '10px'}))
        plot2(df2, selected_year)
