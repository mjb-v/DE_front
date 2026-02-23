import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import re
import requests
from dotenv import load_dotenv
from utils import get_sidebar_filters
from matplotlib import font_manager, rc

font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

load_dotenv()
API_URL = os.getenv("API_URL")

def translate_data(data):
    translation_dict = {
        "month": "월", "date": "가동일자", "process": "공정",
        "line": "라인", "operator": "작업자", "shift": "근무조",
        "model": "모델", "item_number": "품번", "item_name": "품명",
        "specification": "규격", "operating_time": "가동시간",
        "non_operating_time": "비가동시간", "target_quantity": "목표수량",
        "produced_quantity": "생산수량", "production_efficiency": "생산효율", 
        "line_efficiency": "라인가동율", "monthly_production_efficiency": "월별생산효율",
        "monthly_line_efficiency": "월별라인가동율"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

def get_num(text):
    nums = re.findall(r'\d+', str(text))
    return int(nums[0]) if nums else 999
    
def get_prefix(text):
    return re.sub(r'\d+.*', '', str(text)).strip()

def get_efficiency_status(year=None):
    if year is None: year = datetime.today().year
    response = requests.get(f"{API_URL}/productions/efficiency/{year}")
    if response.status_code == 200:
        return translate_data(response.json())
    return pd.DataFrame()

def plot2(df, selected_year):
    fig, ax = plt.subplots(figsize=(10, 6))
    months = df['월']
    bar_width = 0.35
    index = np.arange(len(months))
    ax.bar(index, df['생산효율'], bar_width, label='생산효율', color='b', alpha=0.6)
    ax.bar(index + bar_width, df['라인가동율'], bar_width, label='라인가동율', color='r', alpha=0.6)
    ax.set_xlabel('월', fontsize=12)
    ax.set_ylabel('퍼센트 (%)', fontsize=12)
    ax.set_title(f'{selected_year}년 생산효율과 라인가동율', fontsize=14)
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(months, rotation=45)
    ax.legend()
    st.pyplot(fig)

def get_facility_status_from_db(selected_date):
    date_str = selected_date.strftime('%Y-%m-%d')
    response = requests.get(f"{API_URL}/facility_status/{date_str}")
    
    if response.status_code == 200 and response.json():
        df = pd.DataFrame(response.json())
        df['라인가동률(%)'] = (df['operating_time'] / 24) * 100
        df['라인가동률(%)'] = df['라인가동률(%)'].clip(upper=100)
        df['prefix'] = df['line'].apply(get_prefix)
        df['num'] = df['line'].apply(get_num)
        df = df.sort_values(by=['prefix', 'num']).drop(columns=['prefix', 'num'])
        df = df.rename(columns={
            "line": "라인", 
            "produced_quantity": "생산수량",
            "operating_time": "가동시간", 
            "non_operating_time": "비가동시간"
        })
        return df[['라인', '생산수량', '가동시간', '비가동시간', '라인가동률(%)']]
    return pd.DataFrame()

# ----------------------------------------------------------------
def page3_view():
    st.markdown("<h2 style='text-align: left;'>📅 설비 가동 현황 관리</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)

    tab = st.sidebar.radio("메뉴 선택", ["실시간 가동 현황", "연도별 효율 현황"], label_visibility="collapsed")

    if tab == "실시간 가동 현황":
        st.markdown(
            """
            <style>
            .search-box { background-color: #f8f9fa; padding: 20px; border-radius: 5px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
            </style>
            <div class="search-box">
                <h4 style="margin-top:0px; color:#333;">🔍 일별 설비 가동 조회</h4>
            </div>
            """, unsafe_allow_html=True
        )
        
        # 1. 날짜 및 라인 검색
        with st.form("facility_search_form"):
            col1, col2 = st.columns([1, 2])
            with col1:
                selected_date = st.date_input("조회 일자 선택", value=datetime(2026, 2, 14))
            with col2:
                st.text_input("라인 검색 (예: 사출1호기)", key="search_line", placeholder="검색할 라인명을 입력하세요 (비워두면 전체 조회)")
            submit_btn = st.form_submit_button("조회하기", use_container_width=True)
            
        # 2. 데이터 필터링
        df1 = get_facility_status_from_db(selected_date)

        if df1.empty:
            st.warning(f"⚠️ {selected_date.strftime('%Y년 %m월 %d일')}에 해당하는 가동 데이터가 없습니다. (수집된 날짜를 선택해보세요!)")
            return
        search_line_val = st.session_state.get("search_line", "")
        if search_line_val:
            df1 = df1[df1['라인'].str.contains(search_line_val, case=False, na=False)]
            
        if df1.empty:
            st.warning("해당 조건에 맞는 라인 검색 결과가 없습니다.")
            return

        st.markdown(f"**총 {len(df1)}대 설비**의 가동 내역이 조회되었습니다.")
        
        # 3. 테이블 출력
        st.dataframe(
            df1.style.format({
                "생산수량": "{:,.0f} 개",
                "가동시간": "{:,.1f} H",
                "비가동시간": "{:,.1f} H",
                "라인가동률(%)": "{:,.1f} %"
            }),
            use_container_width=True
        )

        st.markdown("---")
        
        # 4. 차트 그래프
        st.subheader(f"📊 {selected_date.strftime('%Y-%m-%d')} 설비별 가동 차트")
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df1['라인'], y=df1['가동시간'], name='가동시간 (H)', marker_color='#4CAF50',
            text=df1['가동시간'].apply(lambda x: f"{x}H" if x > 0 else ""), textposition='inside'
        ))
        fig.add_trace(go.Bar(
            x=df1['라인'], y=df1['비가동시간'], name='비가동시간 (H)', marker_color='#F44336',
            text=df1['비가동시간'].apply(lambda x: f"{x}H" if x > 0 else ""), textposition='inside'
        ))
        fig.add_trace(go.Scatter(
            x=df1['라인'], y=df1['라인가동률(%)'], name='라인가동률 (%)', mode='lines+markers+text',
            marker=dict(color='#FFC107', size=10), line=dict(color='#FFC107', width=3),
            text=df1['라인가동률(%)'].apply(lambda x: f"{x:.1f}%"), textposition='top center', yaxis='y2'
        ))
        
        fig.update_layout(
            barmode='stack', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=30, l=30, r=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
            yaxis=dict(title='시간 (Hours)', range=[0, 26], gridcolor='#e0e0e0'),
            yaxis2=dict(title='가동률 (%)', range=[0, 120], overlaying='y', side='right', showgrid=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        #st.info("💡 **가동률 산출 공식:** [가동시간 ÷ 24시간 × 100]")

    # -------------------------------------------------------------
    # 연도별 효율 현황
    # -------------------------------------------------------------
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
                .dataframe { width: 80% !important; }
                </style>
                """, unsafe_allow_html=True)
            st.dataframe(df2_pivot.style.set_properties(**{'width': '10px'}))
            plot2(df2, selected_year)
        else:
            st.warning(f"{selected_year}년도에 대한 데이터가 없습니다.")