import datetime
import streamlit as st

def get_sidebar_filters(show_month=True):
    """
    사이드바에서 [연도], [월] 선택하는 공통 함수.
    현재 연도/월이 DB 데이터 범위를 벗어나면, 자동으로 DB의 마지막 연도/월로 고정함.
    """
    now = datetime.datetime.now()
    current_year = now.year

    default_year = current_year
    default_month = now.month

    year_list = list(range(2014, current_year + 1))

    selected_year = st.sidebar.selectbox(
        "연도 선택", 
        year_list, 
        index=year_list.index(default_year)
    )

    if show_month:
        selected_month = st.sidebar.selectbox(
            "월 선택", 
            list(range(1, 13)), 
            index=default_month - 1
        )
        return selected_year, selected_month
    else:
        return selected_year