# 생산관리 2. 생산실적관리
import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
from datetime import datetime
from natsort import natsorted
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")

# 한글 컬럼명으로 변환
def translate_data(data):
    translation_dict = {
        "date": "날짜",
        "item_number": "품번",
        "item_name": "품명",
        "line": "라인",
        "operator": "작업자",
        "model": "모델",
        "target_quantity": "목표수량",
        "produced_quantity": "생산수량",
        "production_efficiency": "생산효율",
        "operating_time": "가동시간",
        "non_operating_time": "비가동시간",
        "line_efficiency": "설비효율"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

def get_production_data(start_date, end_date, operator, item_number, item_name):
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'operator': operator,
        'item_number': item_number,
        'item_name': item_name
    }
    response = requests.get(f"{API_URL}/productions/days/", params=params)
    if response.status_code == 200:
        return translate_data(response.json())
    else:
        st.error("데이터를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

# ------------------------------------------------------------------------------------------------
def page2_view():
    st.markdown("<h2 style='text-align: left;'>📈 생산 실적 관리</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)

    st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>필터 설정</div>", unsafe_allow_html=True)
    today = datetime.today()
    last_day = calendar.monthrange(today.year, today.month)[1]

    start_date = st.sidebar.date_input('시작 날짜', value=datetime(today.year, today.month, 1))
    end_date = st.sidebar.date_input('종료 날짜', value=datetime(today.year, today.month, last_day))
    operator = st.sidebar.text_input('작업자 이름 입력')
    item_number = st.sidebar.text_input('품번 입력')
    item_name = st.sidebar.text_input('품명 입력')

    if 'df' not in st.session_state or st.sidebar.button('검색'):
        df = get_production_data(start_date, end_date, operator, item_number, item_name)
        if not df.empty:
            selected_columns = ["날짜", "품번", "품명", "라인", "작업자", "모델", "생산수량", "생산효율", "가동시간", "설비효율"]
            df = df[selected_columns]
            st.session_state['df'] = df
        else:
            st.warning("검색 결과가 없습니다.")
            if 'df' in st.session_state:
                del st.session_state['df']  # 검색 결과가 없을 때 세션에서 데이터 삭제

    if 'df' in st.session_state:
        df = st.session_state['df']
        st.dataframe(df)
        lines = natsorted(df['라인'].unique().tolist())  # 라인을 숫자로 정렬
        num_columns = 4

        # < 생산효율 >
        on_production = st.toggle("평균 생산효율 보기", value=True)

        selected_lines_efficiency = []
        cols = st.columns(num_columns)
        default_checked_lines = ["Line1", "Line2", "Line3"]

        for i, line in enumerate(lines):
            col = cols[i % num_columns]
            checked = line in default_checked_lines
            if col.checkbox(f'{line}', value=checked, key=f"line_production_{line}"):
                selected_lines_efficiency.append(line)

        if on_production:  # 토글 ON: 평균 생산효율 라인 그래프
            st.subheader('라인별 평균 생산효율')

            filtered_data_efficiency = df[df['라인'].isin(selected_lines_efficiency)]
            grouped_data_efficiency = (
                filtered_data_efficiency.groupby(['날짜', '라인'], as_index=False)
                .agg({'생산효율': 'mean'})
            )

            fig_efficiency = px.line(
                grouped_data_efficiency, 
                x='날짜', 
                y='생산효율', 
                color='라인',
                markers=True
            )
            fig_efficiency.update_xaxes(tickformat='%b %d')
            st.plotly_chart(fig_efficiency)

        else:  # 토글 OFF: 생산효율 박스플롯
            st.subheader('라인별 생산효율')

            filtered_data_production = df[df['라인'].isin(selected_lines_efficiency)]

            fig_production = px.box(
                filtered_data_production, 
                x='날짜', 
                y='생산효율', 
                color='라인',
            )
            fig_production.update_xaxes(tickformat='%b %d')
            st.plotly_chart(fig_production)


        # < 설비효율 >
        on_equipment = st.toggle("평균 설비효율 보기", value=True)

        selected_lines_equipment = []
        cols_equipment = st.columns(num_columns)

        for i, line in enumerate(lines):
            col = cols_equipment[i % num_columns]
            checked = line in default_checked_lines
            if col.checkbox(f'{line}', value=checked, key=f"line_equipment_{line}"):
                selected_lines_equipment.append(line)

        if on_equipment:  # 토글 ON: 평균 설비효율 라인 그래프
            st.subheader('라인별 평균 설비효율')

            filtered_data_equipment = df[df['라인'].isin(selected_lines_equipment)]
            grouped_data_equipment = (
                filtered_data_equipment.groupby(['날짜', '라인'], as_index=False)
                .agg({'설비효율': 'mean'})
            )

            fig_equipment = px.line(
                grouped_data_equipment, 
                x='날짜', 
                y='설비효율', 
                color='라인',
                markers=True
            )
            fig_equipment.update_xaxes(tickformat='%b %d')
            st.plotly_chart(fig_equipment)

        else:  # 토글 OFF: 설비효율 박스플롯
            st.subheader('라인별 설비효율')

            filtered_data_equipment = df[df['라인'].isin(selected_lines_equipment)]

            fig_equipment_box = px.box(
                filtered_data_equipment, 
                x='날짜', 
                y='설비효율', 
                color='라인',
            )
            fig_equipment_box.update_xaxes(tickformat='%b %d')
            st.plotly_chart(fig_equipment_box)

    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 2px 0;'>", unsafe_allow_html=True)
    st.markdown("**Note:** 그래프는 각 날짜의 라인별 평균 생산효율과 설비효율을 계산한 값입니다.")