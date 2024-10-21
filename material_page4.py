# 자재관리 4. LOT재고관리

from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

# FastAPI URL
load_dotenv()
API_URL = os.getenv("API_URL")

# 한글 컬럼명으로 변환
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

    df = get_material_LOT_inventory_data().drop(columns=["id", "account_idx"])
    st.dataframe(df)
