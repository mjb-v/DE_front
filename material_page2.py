# 자재관리 2. 자재입고관리
from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from get_companies_list import company_names
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
        "purchase_category": "매입구분"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

# 데이터 테이블
def get_material_inventory_data():
    response = requests.get(f"{API_URL}/materials_in_out/all/")
    if response.status_code == 200:
        data = response.json()
        return translate_data(data)
    else:
        st.error("자재입고관리 데이터를 가져오는 데 실패했습니다.")
        return None

# 등록
def create_material_inventory_data(data):
    response = requests.post(f"{API_URL}/materials_in_out/", json=data)
    if response.status_code == 200:
        st.success("성공적으로 저장되었습니다!")
    else:
        st.error("저장에 실패했습니다.")

# 수정
def update_material_inventory_data(material_id, data):
    response = requests.put(f"{API_URL}/materials_in_out/{material_id}", json=data)
    if response.status_code == 200:
        st.success("성공적으로 수정되었습니다!")
    else:
        st.error("수정에 실패했습니다.")

# 삭제
def delete_material_inventory_data(material_id):
    response = requests.delete(f"{API_URL}/materials_in_out/{material_id}")
    if response.status_code == 200:
        st.success("성공적으로 삭제되었습니다!")
    else:
        st.error("삭제에 실패했습니다.")

# 수정사항 입력 필드
def material_inout_plan_form(selected_date=None, statement_number="", client="", delivery_quantity=0, defective_quantity=0, settlement_quantity=0, supply_amount=0, vat=0, total_amount=0, purchase_category="구매입고"):

    if selected_date is None:
        selected_date = datetime.today().date()

    selected_date = st.date_input("날짜 선택", value=selected_date)

    statement_number = st.text_input("전표번호", statement_number)
    client = st.selectbox("거래처명", options=company_names, index=company_names.index(client) if client in company_names else 0)
    delivery_quantity = st.number_input("납품수량", min_value=0, value=delivery_quantity)
    defective_quantity = st.number_input("불량수량", min_value=0, value=defective_quantity)
    settlement_quantity = st.number_input("정산수량", min_value=0, value=settlement_quantity)
    supply_amount = st.number_input("공급가액", min_value=0, value=supply_amount)
    vat = st.number_input("부가세", min_value=0, value=vat)
    total_amount = st.number_input("합계", min_value=0, value=total_amount)
    purchase_category = st.text_input("매입구분", purchase_category)
    
    return selected_date, statement_number, client, delivery_quantity, defective_quantity, settlement_quantity, supply_amount, vat, total_amount, purchase_category

# 페이지 전환
def go_to_page(page_name):
    st.session_state.page = page_name

# 메인 페이지
def main_page():
    st.markdown("<h2 style='text-align: left;'>📥 자재 입고 관리</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)

    df = get_material_inventory_data()
    df_display = df.drop(columns=["id", "account_idx"])
    st.dataframe(df_display)

    col1, col2 = st.columns([2, 1])
    with col1:
            selected_index = st.selectbox("수정/삭제할 줄의 번호 선택", df.index, key="select_index")
    with col2:
        selected_row = df.loc[selected_index]
        material_id = selected_row["id"]

        st.session_state.selected_row = selected_row
        st.session_state.material_id = material_id

        st.button('수정', on_click=go_to_page, args=('edit',))

        if st.button("삭제", key="delete_button"):
            delete_material_inventory_data(material_id)
            st.rerun()

    # 등록
    st.markdown(
    """
    <style>
    .create-header {
        background-color: #e0ffe0;  /* 밝은 녹색 배경 */
        padding: 10px;
        border-radius: 5px;
        font-size: 1.5rem;
        font-weight: bold;
    }
    </style>
    <div class="create-header">자재 입고 등록</div>
    """, 
    unsafe_allow_html=True
    )

    with st.form(key="create_form"):
        new_date, new_statement_number, new_client, new_delivery_quantity, new_defective_quantity, new_settlement_quantity, new_supply_amount, new_vat, new_total_amount, new_purchase_category = material_inout_plan_form()

        if st.form_submit_button("저장"):
            new_data = {
                "date": new_date.strftime("%Y-%m-%d"),
                "statement_number": new_statement_number,
                "client": new_client,
                "delivery_quantity": new_delivery_quantity,
                "defective_quantity": new_defective_quantity,
                "settlement_quantity": new_settlement_quantity,
                "supply_amount": new_supply_amount,
                "vat": new_vat,
                "total_amount": new_total_amount,
                "purchase_category": new_purchase_category
            }
            create_material_inventory_data(new_data)
            st.rerun()

def edit_page():
    selected_row = st.session_state.selected_row
    material_id = st.session_state.material_id

    st.markdown(
        """
        <style>
        .edit-header {
            background-color: #f0f8ff;  /* 밝은 파란색 배경 */
            padding: 10px;
            border-radius: 5px;
            font-size: 1.5rem;
            font-weight: bold;
        }
        </style>
        <div class="edit-header">테이블 수정</div>
        """, 
        unsafe_allow_html=True
    )

    with st.form(key='edit_form'):
        selected_date = datetime.strptime(selected_row['날짜'], "%Y-%m-%d").date()

        update_date, update_statement_number, update_client, update_delivery_quantity, update_defective_quantity, update_settlement_quantity, update_supply_amount, update_vat, update_total_amount, update_purchase_category = material_inout_plan_form(
            selected_date,
            selected_row['전표번호'],
            selected_row['거래처명'],
            int(selected_row['납품수량']),
            int(selected_row['불량수량']),
            int(selected_row['정산수량']),
            int(selected_row['공급가액']),
            int(selected_row['부가세']),
            int(selected_row['합계']),
            selected_row['매입구분']
        )
        form_submitted = st.form_submit_button("저장")
    st.button('뒤로가기', on_click=go_to_page, args=('main',))

    if form_submitted:
        update_data = {
            "date": update_date.strftime("%Y-%m-%d"),
            "statement_number": update_statement_number,
            "client": update_client,
            "delivery_quantity": update_delivery_quantity,
            "defective_quantity": update_defective_quantity,
            "settlement_quantity": update_settlement_quantity,
            "supply_amount": update_supply_amount,
            "vat": update_vat,
            "total_amount": update_total_amount,
            "purchase_category": update_purchase_category
        }
        update_material_inventory_data(material_id, update_data)
        st.session_state.page = 'main'
        st.rerun()

# ----------------------------------------------------------------
def material_page2_view():
    if 'page' not in st.session_state:
        st.session_state.page = 'main'

    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'edit':
        edit_page()