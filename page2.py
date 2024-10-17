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

# ----------------------------------------------------------------
def page2_view():
    st.title("생산 실적 관리")

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
        st.write("검색 결과:")
        st.dataframe(df)
        lines = natsorted(df['라인'].unique().tolist()) # 라인을 숫자로 정렬

        # 라인별 체크박스 가로로 배치
        st.subheader('라인별 생산효율')
        selected_lines_efficiency = []
        num_columns = 4
        cols = st.columns(num_columns)

        for i, line in enumerate(lines):
            col = cols[i % num_columns]
            if col.checkbox(f'{line}', value=True):
                selected_lines_efficiency.append(line)
        
        filtered_data_efficiency = df[df['라인'].isin(selected_lines_efficiency)]

        # 생산효율 그래프
        fig_efficiency = px.line(
            filtered_data_efficiency, 
            x='날짜', 
            y='생산효율', 
            color='라인', 
            title='라인별 생산효율',
            markers=True
        )
        fig_efficiency.update_xaxes(tickformat='%b %d')
        st.plotly_chart(fig_efficiency)

        # 라인별 체크박스 - 설비효율
        st.subheader('라인별 설비효율')
        selected_lines_equipment = []
        cols_equipment = st.columns(num_columns)

        for i, line in enumerate(lines):
            col = cols_equipment[i % num_columns]
            if col.checkbox(f'{line}', value=True, key=f"equipment_{line}"):
                selected_lines_equipment.append(line)

        filtered_data_equipment = df[df['라인'].isin(selected_lines_equipment)]

        # 설비효율 그래프
        fig_equipment = px.line(
            filtered_data_equipment, 
            x='날짜', 
            y='설비효율', 
            color='라인', 
            title='라인별 설비효율',
            markers=True
        )
        fig_equipment.update_xaxes(tickformat='%b %d')
        st.plotly_chart(fig_equipment)

if __name__ == "__main__":
    page2_view()
