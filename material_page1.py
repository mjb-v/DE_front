# 자재계획관리

from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from get_companies_list import company_names

font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

# FastAPI URL
load_dotenv()
API_URL = os.getenv("API_URL")

# 한글 컬럼명으로 변환
def translate_data(data):
    translation_dict = {
        "year": "년도",
        "month": "월",
        "date": "날짜",
        "business_plan": "사업계획",
        "business_amount": "실적",
        "business_achievement_rate": "사업달성율",
        "item_number": "품번",
        "item_name": "품명",
        "client_code": "거래처코드",
        "previous_amount": "전월실적",
        "current_amount": "당월실적",
        "growth_rate": "증감율",
        "prod_plan": "생산계획",
        "prod_amount": "생산실적",
        "production_achievement_rate": "생산달성율",
        "client": "거래처명", # (dropdown: (주)금성오토텍, 
        "model": "모델구분", # (dropdown: 가정, 건조기, 세탁기, 식기세척기, 에어컨, 중장비)
        "item_category": "품목구분", # (dropdown: 원재료, 부재료, 재공품, 제품, 반제품)
        "process": "공정구분", # (drodown: 검사/조립, 사출)
        "quantity": "계획수량"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

# 1-1. 위 - 전체 플랜 GET
def get_all_plan(year: int):
    response = requests.get(f"{API_URL}/plans/rate/{year}")
    if response.status_code == 200:
        data = response.json()
        df = translate_data(data)
        df = df.drop(columns=["년도", "생산계획", "생산실적", "생산달성율"])
        df_pivot = df.set_index('월').T
        df_pivot.columns = [f"{month}월" for month in df_pivot.columns]
        row_order = ["사업계획", "사업실적", "사업달성율"]
        df_pivot = df_pivot.reindex(row_order)
        return df_pivot
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

# 1-2. 아래 - 당월 플랜
def get_material_all_plan(year: int, month: int):
    response = requests.get(f"{API_URL}/materials/rate/{year},{month}")
    if response.status_code == 200:
        data = response.json()
        df = translate_data(data)
        return df
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

# 2-1. 등록 페이지 전체 테이블 보여주기 GET
def get_plan_register():
    response = requests.get(f"{API_URL}/materials/all/")
    if response.status_code == 200:
        data = response.json()
        df = translate_data(data)
        return df
    else:
        st.error("전체 생산 계획 리스트를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

# 2-2. 자재관리계획 저장 POST
def create_production_plan(data):
    response = requests.post(f"{API_URL}/materials/", json=data)
    if response.status_code == 200:
        st.success("생산 계획이 성공적으로 저장되었습니다!")
        st.session_state['refresh_table'] = True
    else:
        st.error("생산 계획 저장에 실패했습니다.")

# 2-3. 자재관리계획 수정 PUT
def update_production_plan(material_id, data):
    response = requests.put(f"{API_URL}/materials/{material_id}", json=data)
    if response.status_code == 200:
        st.success("생산 계획이 성공적으로 수정되었습니다!")
        st.session_state['refresh_table'] = True
    else:
        st.error("생산 계획 수정에 실패했습니다.")

# 2-4. 자재관리계획 삭제 DELETE
def delete_production_plan(material_id):
    response = requests.delete(f"{API_URL}/materials/{material_id}")
    if response.status_code == 200:
        st.success("생산 계획이 성공적으로 삭제되었습니다!")
        st.session_state['refresh_table'] = True
    else:
        st.error("생산 계획 삭제에 실패했습니다.")

# 2. 자재관리계획 입력 필드
def production_plan_form(client = "", item_number="", item_name="", item_category="원재료", model="가전", year=2024, month=1, inventory=0, form_key=""):
    client = st.selectbox("거래처명", options=company_names, index=company_names.index(model), key=f"company_names{form_key}")
    item_number = st.text_input("품번 입력", item_number, key=f"item_number_{form_key}")
    item_name = st.text_input("품명 입력", item_name, key=f"item_name_{form_key}")

    category_options = ["원재료", "부재료", "재공품", "제품", "반제품"]
    model_options = ["가전", "건조기", "세탁기", "식기세척기", "에어컨", "중장비", "포장박스", "LX2PE", "GEN3.5", "MX5"]
    item_category = st.selectbox("품목 선택", options=category_options, index=category_options.index(model), key=f"item_category{form_key}")
    model = st.selectbox("모델 선택", options=model_options, index=model_options.index(model), key=f"model_{form_key}")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        year = st.selectbox("년도 선택", options=list(range(2014, 2100)), index=year - 2014, key=f"year_{form_key}")
    with col2:
        month = st.selectbox("월 선택", options=list(range(1, 13)), index=month - 1, key=f"month_{form_key}")
    inventory = st.number_input("계획 수량", min_value=0, value=inventory, key=f"inventory_{form_key}")

    return client, item_number, item_name, item_category, model, year, month, inventory

# ----------------------------------------------------------------
def material_page1_view():
    st.title("자재 계획 관리")
    tab = st.sidebar.selectbox("", ["자재 계획 관리", "자재 계획 등록"])

    if tab == "자재 계획 관리":
        st.subheader("자재 계획")
        selected_year = st.sidebar.selectbox("년도 선택", list(range(2014, 2025)))
        df = get_all_plan(selected_year)
        st.subheader(f"{selected_year}년도 계획 및 실적 데이터")
        st.dataframe(df)