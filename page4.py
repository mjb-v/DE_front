# 생산관리 4. 재고관리

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# FastAPI URL
load_dotenv()
API_URL = os.getenv("API_URL")

# 한글 컬럼명으로 변환
def translate_data(data):
    translation_dict = {
        "date": "날짜",
        "item_number": "품번",
        "item_name": "품명",
        "price": "단가",
        "basic_quantity": "기초수량",
        "basic_amount": "기초금액",
        "in_quantity": "입고수량",
        "in_amount": "입고금액",
        "defective_in_quantity": "입고불량수량",
        "defective_in_amount": "입고불량금액",
        "out_quantity": "출고수량",
        "out_amount": "출고금액",
        "adjustment_quantity": "조정수량",
        "current_quantity": "현재고수량",
        "current_amount": "현재고금액",
        "lot_current_quantity": "LOT현재고",
        "difference_quantity": "차이수량"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

def get_inventory_data(year: int, month: int):
    params = {"year": year, "month": month}
    response = requests.get(f"{API_URL}/inventories/month/", params=params)
    if response.status_code == 200:
        data = response.json()
        return translate_data(data)
    else:
        st.error("재고관리 데이터를 가져오는 데 실패했습니다.")
        return None

# ----------------------------------------------------------------
def page4_view():
    st.title("재고 관리")
    st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>필터 설정</div>", unsafe_allow_html=True)

    current_year = datetime.today().year
    current_month = datetime.today().month
    selected_year = st.sidebar.selectbox("년도 선택", list(range(2014, 2025)), index=list(range(2014, 2025)).index(current_year))
    selected_month = st.sidebar.selectbox("월 선택", list(range(1, 13)), index=list(range(1, 13)).index(current_month))

    df = get_inventory_data(selected_year, selected_month)
    if df is not None and not df.empty:
        df = df.drop(columns=["id", "account_idx"], errors="ignore")
        st.subheader(f"{selected_year}년 {selected_month}월")
        st.dataframe(df)
    else:
        st.warning(f"{selected_year}년 {selected_month}월에 대한 데이터가 없습니다.")