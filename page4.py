# 재고관리 - POST 추가 예정

import streamlit as st
import pandas as pd
import requests

# FastAPI URL
API_URL = "http://127.0.0.1:8000"

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
    url = f"{API_URL}/inventories/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("데이터를 가져오는 데 실패했습니다.")
        return None

def page4_view():
    st.title("재고 관리 페이지")
    data = get_inventory_data()

    if data:
        df = translate_data(data)
        st.dataframe(df)

if __name__ == "__main__":
    page4_view()
