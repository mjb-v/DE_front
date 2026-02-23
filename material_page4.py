# 자재관리 4. LOT재고관리

from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from get_companies_list import company_names

font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

load_dotenv()
API_URL = os.getenv("API_URL")

def translate_data(data):
    translation_dict = {
        "date": "날짜",
        "item_number": "품번",
        "item_name": "품명",
        "item_category": "품목",
        "model": "모델",
        "price": "단가",
        "process": "공정",
        "client": "거래처명",
        "overall_status_quantity": "전체현황-수량",
        "overall_status_amount": "전체현황-금액"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

def get_material_LOT_inventory_data():
    response = requests.get(f"{API_URL}/material_LOT/all/")
    if response.status_code == 200:
        data = response.json()
        return translate_data(data)
    else:
        st.error("LOT 재고관리 데이터를 가져오는 데 실패했습니다.")
        return None

# ----------------------------------------------------------------
def material_page4_view():
    st.markdown("<h2 style='text-align: left;'>🔢 LOT 재고 관리</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)

    df = get_material_LOT_inventory_data()
    
    if df is not None and not df.empty:
        df = df.drop(columns=["materialinven_idx", "account_idx"], errors="ignore")
        
        # -------------------------------------------------------------
        # 🔍 검색/조회
        # -------------------------------------------------------------
        st.markdown(
            """
            <style>
            .search-box {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                border: 1px solid #e0e0e0;
                margin-bottom: 20px;
            }
            </style>
            <div class="search-box">
                <h4 style="margin-top:0px; color:#333;">🔍 검색/조회</h4>
            </div>
            """, unsafe_allow_html=True
        )

        client_options = ["전체"] + company_names
        model_options = ["전체"] + sorted(list(df['모델'].dropna().unique()))

        with st.form("lot_search_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                search_client = st.selectbox("거래처명", options=client_options)
            with col2:
                search_model = st.selectbox("모델", options=model_options)
            with col3:
                search_item_no = st.text_input("품번 검색", placeholder="예: 11")
            with col4:
                search_item_name = st.text_input("품명 검색", placeholder="예: 세탁기")
                
            submit_btn = st.form_submit_button("조회하기", use_container_width=True)

        # -------------------------------------------------------------
        # ⚙️ 필터 적용
        # -------------------------------------------------------------
        filtered_df = df.copy()
        
        if search_client != "전체":
            filtered_df = filtered_df[filtered_df['거래처명'] == search_client]
        if search_model != "전체":
            filtered_df = filtered_df[filtered_df['모델'] == search_model]
        if search_item_no:
            filtered_df = filtered_df[filtered_df['품번'].astype(str).str.contains(search_item_no, na=False, case=False)]
        if search_item_name:
            filtered_df = filtered_df[filtered_df['품명'].astype(str).str.contains(search_item_name, na=False, case=False)]

        # -------------------------------------------------------------
        # 📊 테이블
        # -------------------------------------------------------------
        st.markdown(f"총 **{len(filtered_df)}**건의 LOT 재고 내역이 조회되었습니다.")
        
        if not filtered_df.empty:
            numeric_cols = filtered_df.select_dtypes(include=['number']).columns
            format_dict = {col: "{:,.0f}" for col in numeric_cols}
            
            st.dataframe(filtered_df.style.format(format_dict), use_container_width=True)
        else:
            st.info("검색 조건에 맞는 LOT 재고 데이터가 없습니다.")
            
    else:
        st.warning("등록된 LOT 재고관리 데이터가 없습니다.")