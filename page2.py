import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
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
        "equipment_efficiency": "설비효율"
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
    st.title("생산실적 조회")

    st.sidebar.title("필터 설정")
    start_date = st.sidebar.date_input('시작 날짜', value=datetime(2024, 9, 1))
    end_date = st.sidebar.date_input('종료 날짜', value=datetime(2024, 9, 30))
    operator = st.sidebar.text_input('작업자 이름 입력')
    item_number = st.sidebar.text_input('품번 입력')
    item_name = st.sidebar.text_input('품명 입력')

    if st.sidebar.button('검색'):
        df = get_production_data(start_date, end_date, operator, item_number, item_name)
        if not df.empty:
            selected_columns = ["날짜", "품번", "품명", "라인", "작업자", "모델", "생산수량", "생산효율", "가동시간", "설비효율"]
            df = df[selected_columns]
            st.session_state['df'] = df
        else:
            st.warning("검색 결과가 없습니다.")

    if 'df' in st.session_state:
        df = st.session_state['df']
        st.write("검색 결과:")
        st.dataframe(df)
        lines = df['라인'].unique().tolist()

        # 그래프 - 생산효율
        st.subheader('라인별 생산효율')
        selected_lines_efficiency = st.multiselect('라인 선택 (생산효율)', lines, default=lines)
        filtered_data_efficiency = df[df['라인'].isin(selected_lines_efficiency)]

        fig_efficiency = px.line(
            filtered_data_efficiency, 
            x='날짜', 
            y='생산효율', 
            color='라인', 
            title='라인별 생산효율',
            markers=True
        )
        st.plotly_chart(fig_efficiency)

        # 그래프 - 설비효율
        st.subheader('라인별 설비효율')
        selected_lines_equipment = st.multiselect('라인 선택 (설비효율)', lines, default=lines)
        filtered_data_equipment = df[df['라인'].isin(selected_lines_equipment)]

        fig_equipment = px.line(
            filtered_data_equipment, 
            x='날짜', 
            y='설비효율', 
            color='라인', 
            title='라인별 설비효율',
            markers=True
        )
        st.plotly_chart(fig_equipment)

if __name__ == "__main__":
    page2_view()