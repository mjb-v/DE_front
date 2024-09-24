import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests

API_URL = "http://127.0.0.1:8000/productions"
def get_production_data(start_date, end_date, operator, part_number, part_name):
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'operator': operator,
        'part_number': part_number,
        'part_name': part_name
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("백엔드에서 데이터를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

def page2_view():
    st.title("생산실적 조회")

    st.sidebar.title("필터 설정")
    start_date = st.sidebar.date_input('시작 날짜', value=datetime(2024, 8, 1))
    end_date = st.sidebar.date_input('종료 날짜', value=datetime(2024, 8, 31))
    operator = st.sidebar.text_input('작업자 이름 입력')
    part_number = st.sidebar.text_input('품번 입력')
    part_name = st.sidebar.text_input('품명 입력')

    if st.sidebar.button('검색'):
        df = get_production_data(start_date, end_date, operator, part_number, part_name)
        if not df.empty:
            st.session_state['df'] = df
        else:
            st.warning("검색 결과가 없습니다.")

    if 'df' in st.session_state:
        df = st.session_state['df']
        st.write("검색 결과:")
        st.dataframe(df)
        lines = df['line'].unique().tolist()

        # 그래프 - 생산효율
        st.subheader('라인별 생산효율')
        selected_lines_efficiency = st.multiselect('라인 선택 (생산효율)', lines, default=lines)
        filtered_data_efficiency = df[df['line'].isin(selected_lines_efficiency)]

        fig_efficiency = px.line(
            filtered_data_efficiency, 
            x='date', 
            y='production_efficiency', 
            color='line', 
            title='라인별 생산효율',
            markers=True
        )
        st.plotly_chart(fig_efficiency)

        # 그래프 - 설비효율
        st.subheader('라인별 설비효율')
        selected_lines_equipment = st.multiselect('라인 선택 (설비효율)', lines, default=lines)
        filtered_data_equipment = df[df['line'].isin(selected_lines_equipment)]

        fig_equipment = px.line(
            filtered_data_equipment, 
            x='date', 
            y='equipment_efficiency', 
            color='line', 
            title='라인별 설비효율',
            markers=True
        )
        st.plotly_chart(fig_equipment)

if __name__ == "__main__":
    page2_view()
