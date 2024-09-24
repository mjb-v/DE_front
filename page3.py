import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
from dotenv import load_dotenv

API_URL = ""
def get_real_time_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("실시간 데이터를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

def page3_view():
    st.title("실시간 가동현황")

    # 사이드바 비우기
    with st.sidebar:
        st.write("")

    # 실시간 테이블과 그래프 공간 설정
    table_placeholder = st.empty()
    graph_placeholder = st.empty()

    # 새로고침 버튼
    if st.button("새로고침"):
        data = get_real_time_data()
        if not data.empty:
            table_placeholder.table(data)
            fig = px.line(
                data, x='Operating Time (hours)', y='Production Quantity', color='line',
                title='라인별 실시간 생산수량'
            )
            graph_placeholder.plotly_chart(fig)
        else:
            st.warning("새로운 실시간 데이터를 가져오지 못했습니다.")
    else:
        # 초기 데이터 로드
        data = get_real_time_data()
        if not data.empty:
            table_placeholder.table(data)
            fig = px.line(
                data, x='Operating Time (hours)', y='Production Quantity', color='line',
                title='라인별 실시간 생산수량'
            )
            graph_placeholder.plotly_chart(fig)
        else:
            st.warning("초기 실시간 가동 데이터가 없습니다.")

if __name__ == "__main__":
    page3_view()
