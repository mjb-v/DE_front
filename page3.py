# 생산관리 3. 생산현황관리

from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
import re
import os
from dotenv import load_dotenv
from utils import get_sidebar_filters

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
        "produced_quantity": "생산수량", 
        "production_efficiency": "생산효율", 
        "line_efficiency": "라인가동율", 
        "monthly_production_efficiency": "월별생산효율",
        "monthly_line_efficiency": "월별라인가동율"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

# 1. GET 실시간 가동 현황 데이터
def get_real_time_status(date=None):
    if date is None:
        date = datetime.today().strftime('%Y-%m-%d')
    else:
        date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')

    response = requests.get(f"{API_URL}/productions/day/{date}")
    if response.status_code == 200:
        data = response.json()
        return translate_data(data)
    else:
        return pd.DataFrame()

# 2. GET 연도별 효율 현황 데이터
def get_efficiency_status(year=None):
    if year is None:
        year = datetime.today().year

    response = requests.get(f"{API_URL}/productions/efficiency/{year}")
    if response.status_code == 200:
        data = response.json()
        return translate_data(data)
    else:
        st.error("효율 현황 데이터를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

# 3. 최근 가동일 감지
def get_latest_date():
    today = datetime.today()
    start_date = today - timedelta(days=30)
    try:
        res = requests.get(f"{API_URL}/productions/days/?start_date={start_date.strftime('%Y-%m-%d')}&end_date={today.strftime('%Y-%m-%d')}")
        if res.status_code == 200 and res.json():
            df_temp = pd.DataFrame(res.json())
            if not df_temp.empty:
                latest = pd.to_datetime(df_temp['date']).max().date()
                return latest
    except:
        pass
    return today - timedelta(days=1)

# 4. 연도별 현황 그래프
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

def get_num(text):
    nums = re.findall(r'\d+', str(text))
    return int(nums[0]) if nums else 999    
def get_prefix(text):
    return re.sub(r'\d+.*', '', str(text)).strip()

# ----------------------------------------------------------------
def page3_view():
    st.markdown("<h2 style='text-align: left;'>📅 생산 현황 관리</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)

    tab = st.sidebar.radio(" ", ["실시간 가동 현황", "연도별 효율 현황"])

    if tab == "실시간 가동 현황":
        st.subheader("실시간 가동 현황")

        latest_date = get_latest_date()
        selected_date = st.sidebar.date_input("조회 일자 선택", value=latest_date)
        
        try:
            formatted_date = selected_date.strftime('%Y-%m-%d')
            df1 = get_real_time_status(formatted_date)

            if df1 is not None and not df1.empty:
                df1_display = df1.drop(columns=['production_idx', 'account_idx'], errors='ignore')
                st.dataframe(df1_display)

                st.markdown("### 라인별 생산 효율")
                df_graph = df1_display[['라인', '생산효율']].copy()
                df_graph['생산효율'] = pd.to_numeric(df_graph['생산효율'], errors='coerce').fillna(0)
                df_grouped = df_graph.groupby('라인').mean().reset_index()     
                df_grouped['prefix'] = df_grouped['라인'].apply(get_prefix)
                df_grouped['num'] = df_grouped['라인'].apply(get_num)
                df_grouped = df_grouped.sort_values(by=['prefix', 'num'])

                fig, ax = plt.subplots(figsize=(10, 5))
                lines = df_grouped['라인'].tolist()
                prod_eff = df_grouped['생산효율'].tolist()

                bars = ax.bar(lines, prod_eff, color='#66b3ff', alpha=0.8, edgecolor='navy', linewidth=1)
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                            f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
                ax.set_xticks(range(len(lines)))
                ax.set_xticklabels(lines, rotation=0) 
                ax.set_ylim(0, 110)
                ax.set_ylabel('생산효율 (%)', fontsize=12)
                ax.set_title(f"{formatted_date} 라인별 평균 생산효율", fontsize=14, pad=15)
                ax.grid(axis='y', linestyle='--', alpha=0.5)
                st.pyplot(fig)

            else:
                st.warning(f"선택하신 날짜 ({formatted_date}) 에 대한 데이터가 없습니다.")

        except Exception as e:
            st.error("오류가 발생했습니다.")
            st.warning(f"세부 오류 메시지: {str(e)}")

    elif tab == "연도별 효율 현황":
        st.subheader("연도별 효율 현황")
        st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>필터 설정</div>", unsafe_allow_html=True)

        selected_year = get_sidebar_filters(show_month=False)

        df2 = get_efficiency_status(selected_year)
        if df2 is not None and not df2.empty:
            df2 = df2.drop(columns=["year"], errors='ignore')
            df2_pivot = df2.set_index('월').T
            df2_pivot.columns = [f"{month}월" for month in df2_pivot.columns]
            st.markdown("""
                <style>
                .dataframe {
                    width: 80% !important;
                }
                </style>
                """, unsafe_allow_html=True)
            st.dataframe(df2_pivot.style.set_properties(**{'width': '10px'}))

            plot2(df2, selected_year)
        else:
            st.warning(f"{selected_year}년도에 대한 데이터가 없습니다.")