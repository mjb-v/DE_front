import datetime
import streamlit as st

def get_sidebar_filters(show_month=True):
    """
    사이드바에서 [연도], [월] 선택하는 공통 함수.
    현재 연도/월이 DB 데이터 범위를 벗어나면, 자동으로 DB의 마지막 연도/월로 고정함.
    """
    now = datetime.datetime.now()
    current_year = now.year

    if current_year > 2024:
        default_year = 2024
        default_month = 11
    else:
        default_year = current_year
        default_month = now.month

    selected_year = st.sidebar.selectbox(
        "연도 선택", 
        list(range(2014, 2025)), 
        index=list(range(2014, 2025)).index(default_year)
    )

    if show_month:
        selected_month = st.sidebar.selectbox(
            "월 선택", 
            list(range(1, 13)), 
            index=list(range(1, 13)).index(default_month)
        )
        return selected_year, selected_month
    else:
        return selected_year