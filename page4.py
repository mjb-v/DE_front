import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")

def translate_data(data):
    translation_dict = {
        "date": "날짜", "item_number": "품번", "item_name": "품명", "price": "단가",
        "basic_quantity": "기초수량", "basic_amount": "기초금액", "in_quantity": "입고수량",
        "in_amount": "입고금액", "defective_in_quantity": "입고불량수량", "defective_in_amount": "입고불량금액",
        "out_quantity": "출고수량", "out_amount": "출고금액", "adjustment_quantity": "조정수량",
        "current_quantity": "현재고수량", "current_amount": "현재고금액", "lot_current_quantity": "LOT현재고",
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
        return None

# ----------------------------------------------------------------
def page4_view():
    st.markdown("<h2 style='text-align: left;'>📦 재고 관리</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)
    
    # -------------------------------------------------------------
    # 🔍 검색/조회
    # -------------------------------------------------------------
    st.markdown(
        """
        <style>
        .search-box { background-color: #f8f9fa; padding: 20px; border-radius: 5px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
        </style>
        <div class="search-box">
            <h4 style="margin-top:0px; color:#333;">🔍 재고 내역 상세 검색</h4>
        </div>
        """, unsafe_allow_html=True
    )

    today = datetime.today()
    year_options = list(range(2015, today.year + 2))
    month_options = list(range(1, 13))

    with st.form("inventory_search_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_year = st.selectbox("조회 연도", options=year_options, index=year_options.index(today.year))
        with col2:
            search_month = st.selectbox("조회 월", options=month_options, index=month_options.index(today.month))
        with col3:
            search_item_no = st.text_input("품번 검색", placeholder="예: 11")
        with col4:
            search_item_name = st.text_input("품명 검색", placeholder="예: 세탁기")
            
        submit_btn = st.form_submit_button("조회하기", use_container_width=True)

    # -------------------------------------------------------------
    # ⚙️ 데이터 불러오기 및 세션 저장
    # -------------------------------------------------------------
    if submit_btn or 'page4_df' not in st.session_state:
        y = search_year if submit_btn else today.year
        m = search_month if submit_btn else today.month
        
        df = get_inventory_data(y, m)
        if df is not None and not df.empty:
            df = df.drop(columns=["inventory_idx", "account_idx"], errors="ignore")
        
        st.session_state['page4_df'] = df if df is not None else pd.DataFrame()
        st.session_state['page4_year'] = y
        st.session_state['page4_month'] = m
        st.session_state['page4_item_no'] = search_item_no if submit_btn else ""
        st.session_state['page4_item_name'] = search_item_name if submit_btn else ""

    df = st.session_state.get('page4_df', pd.DataFrame())
    current_year = st.session_state.get('page4_year', today.year)
    current_month = st.session_state.get('page4_month', today.month)
    item_no_val = st.session_state.get('page4_item_no', "")
    item_name_val = st.session_state.get('page4_item_name', "")

    # -------------------------------------------------------------
    # 📊 테이블
    # -------------------------------------------------------------
    if not df.empty:
        filtered_df = df.copy()
        if item_no_val:
            filtered_df = filtered_df[filtered_df['품번'].astype(str).str.contains(item_no_val, na=False, case=False)]
        if item_name_val:
            filtered_df = filtered_df[filtered_df['품명'].astype(str).str.contains(item_name_val, na=False, case=False)]

        st.markdown(f"**{current_year}년 {current_month}월** | 총 **{len(filtered_df)}**건의 재고 내역이 조회되었습니다.")
        
        if not filtered_df.empty:
            numeric_cols = filtered_df.select_dtypes(include=['number']).columns
            format_dict = {col: "{:,.0f}" for col in numeric_cols}
            st.dataframe(filtered_df.style.format(format_dict), use_container_width=True)
        else:
            st.info("검색 조건에 맞는 재고 데이터가 없습니다.")
    else:
        st.warning(f"⚠️ {current_year}년 {current_month}월에 대한 데이터가 없습니다.")