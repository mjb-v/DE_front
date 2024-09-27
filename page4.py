# 생산관리 4. 재고관리

import streamlit as st
import pandas as pd
import requests
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

def get_inventory_data():
    response = requests.get(f"{API_URL}/inventories/all/")
    if response.status_code == 200:
        data = response.json()
        return translate_data(data)
    else:
        st.error("재고관리 데이터를 가져오는 데 실패했습니다.")
        return None

# ----------------------------------------------------------------
def page4_view():
    st.title("재고 관리")
    df = get_inventory_data().drop(columns=["id", "account_idx"])
    st.dataframe(df)

if __name__ == "__main__":
    page4_view()
