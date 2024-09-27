# 자재관리 2. 자재입고관리

from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

def translate_data(data):
    translation_dict = {
        "date": "날짜",
        "statement_number": "전표번호",
        "client": "거래처명",
        "delivery_quantity": "납품수량",
        "defective_quantity": "불량수량",
        "settlement_quantity": "정산수량",
        "supply_amount": "공급가액",
        "vat": "부가세",
        "total_amount": "합계",
        "purchase_category": " 매입구분"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

def get_material_inventory_data():
    response = requests.get(f"{API_URL}/materials_in_out/all/")
    if response.status_code == 200:
        data = response.json()
        return translate_data(data)
    else:
        st.error("자재입고관리 데이터를 가져오는 데 실패했습니다.")
        return None

# ----------------------------------------------------------------
def material_page2_view():
    st.title("자재 입고 관리")
    df = get_material_inventory_data().drop(columns=["id", "account_idx"])
    st.dataframe(df)
