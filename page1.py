# 생산관리 1. 생산계획관리

from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import time

font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

# FastAPI URL
load_dotenv()
API_URL = os.getenv("API_URL")

# 한글 컬럼명으로 변환
def translate_data(data):
    translation_dict = {
        "year": "연도",
        "month": "월",
        "business_plan": "사업계획",
        "business_amount": "사업실적",
        "business_achievement_rate": "사업달성율",
        "prod_plan": "생산계획",
        "prod_amount": "생산실적",
        "production_achievement_rate": "생산달성율",
        "item_number": "품번",
        "item_name": "품명",
        "model": "모델",
        "price": "단가",
        "inventory": "생산계획",
        "previous_amount": "전월실적",
        "current_amount": "당월실적",
        "growth_rate": "증감율",
        "process": "공정"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

# 1-1. GET 전체 생산 계획 리스트 불러오기 및 가공 ---> 초기 실행 오류 보완, 재시도 및 안정성
@st.cache_data
def get_all_plan(year: int, retries=3, delay=5):
    for i in range(retries):
        try:
            response = requests.get(f"{API_URL}/plans/rate/{year}", timeout=10)
            response.raise_for_status()
            data = response.json()
            df = translate_data(data)
            df = df.drop(columns=["연도"])
            return df
        except requests.exceptions.RequestException as e:
            st.warning(f"데이터를 불러오는데 실패했습니다. 재시도 중... ({i + 1}/{retries})")
            time.sleep(delay)
    st.error("데이터를 불러오는 데 실패했습니다. 나중에 다시 시도해주세요.")
    return None

# 1-2. 아래 - 당월 플랜
def get_monthly_plan(year: int, month: int):
    response = requests.get(f"{API_URL}/plans/rates/{year},{month}")
    if response.status_code == 200:
        data = response.json()
        if data:
            df = translate_data(data)
            return df
        else:
            st.warning(f"{year}년 {month}월에 해당하는 데이터가 없습니다.")
            return pd.DataFrame()
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

# 2-1. GET 등록 페이지 테이블 데이터
def get_plan_register():
    response = requests.get(f"{API_URL}/plans/all/")
    if response.status_code == 200:
        data = response.json()
        df = translate_data(data)

        # '날짜' 컬럼 생성
        df['날짜'] = df.apply(lambda row: f"{int(row['연도'])}-{int(row['월']):02d}", axis=1)
        df = df.drop(columns=["연도", "월", "account_idx"])

        return df
    else:
        st.error("전체 생산 계획 리스트를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

# 2-2. POST 생산 계획 저장
def create_production_plan(data):
    response = requests.post(f"{API_URL}/plans/", json=data)
    if response.status_code == 200:
        st.success("생산 계획이 성공적으로 저장되었습니다!")
    else:
        st.error("생산 계획 저장에 실패했습니다.")

# 2-3. PUT 생산 계획 수정
def update_production_plan(plan_id, data):
    response = requests.put(f"{API_URL}/plans/{plan_id}", json=data)
    if response.status_code == 200:
        st.success("생산 계획이 성공적으로 수정되었습니다!")
    else:
        st.error("생산 계획 수정에 실패했습니다.")

# 2-4. DELETE 생산 계획 삭제
def delete_production_plan(plan_id):
    response = requests.delete(f"{API_URL}/plans/{plan_id}")
    if response.status_code == 200:
        st.success("생산 계획이 성공적으로 삭제되었습니다!")
    else:
        st.error("생산 계획 삭제에 실패했습니다.")

# 2. 생산계획 입력 필드
def production_plan_form(year=2024, month=10, item_number="", item_name="", model="가전", price=0, inventory=0, process="사출", form_key=""):
    model_options = ["가전", "건조기", "세탁기", "식기세척기", "에어컨", "중장비", "포장박스", "LX2PE", "GEN3.5", "MX5"]
    process_options = ["사출", "검사/조립"]

    today = datetime.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    col1, col2 = st.columns([1, 1])
    with col1:
        year = st.selectbox("연도", options=list(range(2014, 2100)), index=year - 2014, key=f"year_{form_key}")
    with col2:
        month = st.selectbox("월", options=list(range(1, 13)), index=month - 1, key=f"month_{form_key}")

    item_number = st.text_input("품번", item_number, key=f"item_number_{form_key}")
    item_name = st.text_input("품명", item_name, key=f"item_name_{form_key}")
    model = st.selectbox("모델", options=model_options, index=model_options.index(model), key=f"model_{form_key}")
    price = st.number_input("단가", min_value=0, value=price, key=f"price_{form_key}")
    inventory = st.number_input("생산 계획 수량", min_value=0, value=inventory, key=f"inventory_{form_key}")
    process = st.selectbox("공정", options=process_options, index=process_options.index(process), key=f"process_{form_key}")
    
    return year, month, item_number, item_name, model, price, inventory, process

# ------------------------------------------------------------------------------------

def page1_view():
    st.markdown("<h2 style='text-align: left;'>📝 생산 계획 관리</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)

    tab = st.sidebar.radio(" ", ["생산 계획 조회", "생산 계획 등록/수정"])

    # 1. 생산 계획 조회 페이지
    if tab == "생산 계획 조회":
        st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>필터 설정</div>", unsafe_allow_html=True)

        current_year = datetime.today().year
        current_month = datetime.today().month
        selected_year = st.sidebar.selectbox("연도 선택", list(range(2014, 2025)), index=list(range(2014, 2025)).index(current_year))
        selected_month = st.sidebar.selectbox("월 선택", list(range(1, 13)), index=list(range(1, 13)).index(current_month))

        df = get_all_plan(selected_year)
        # 테이블 형식으로 변환 (month를 columns로, 나머지를 index로 변환, row 순서 정렬)
        df1 = df.set_index('월').T
        df1.columns = [f"{month}월" for month in df1.columns]
        row_order = ["사업계획", "사업실적", "사업달성율", "생산계획", "생산실적", "생산달성율"]
        df1 = df1.reindex(row_order)
        st.subheader(f"{selected_year}년도 계획 및 실적 데이터")
        st.dataframe(df1)

        df2 = get_monthly_plan(selected_year, selected_month)
        if df2.empty:
            pass
        else:
            st.subheader(f"{selected_year}년 {selected_month}월")
            df2 = df2.drop(columns=['연도','월'])
            st.dataframe(df2)

        # 그래프
        business_achievement_rates = df["사업달성율"]
        production_achievement_rates = df["생산달성율"]
        months = df["월"].apply(lambda x: f"{x}월")
        fig, ax = plt.subplots(figsize=(8, 6))

        # 막대그래프에 월별 데이터 추가
        ax.bar(months, business_achievement_rates, width=0.4, label='사업 달성률', align='center', color='#ff9999')
        ax.bar(months, production_achievement_rates, width=0.4, label='생산 달성률', align='edge', color='#66b3ff')

        # 그래프에 텍스트와 제목 추가
        ax.set_ylim(0, 100)
        ax.set_ylabel('달성률 (%)')
        ax.set_title(f"{selected_year}년 월별 사업 및 생산 달성률")
        ax.legend()
        st.pyplot(fig)

    # 2. 생산 계획 등록/수정 페이지
    elif tab == "생산 계획 등록/수정":
        df = get_plan_register()
        if not df.empty:
            df_display = df.drop(columns=["plan_idx"])[['날짜', '품번', '품명', '모델', '단가', '생산계획', '공정']]
            st.dataframe(df_display)

        # 수정/삭제할 행 선택 및 버튼 배치
        st.subheader("수정/삭제")
        col1, col2 = st.columns([2, 1])

        with col1:
                selected_index = st.selectbox("수정/삭제할 줄의 번호 선택", df.index, key="select_index")

        with col2:
            selected_row = df.loc[selected_index]
            prod_id = selected_row["plan_idx"]

            # 수정 버튼
            if st.button("수정", key="edit_button"):
                st.session_state['is_editing'] = True

            # 삭제 버튼
            if st.button("삭제", key="delete_button"):
                delete_production_plan(prod_id)
                st.rerun()

        # 수정할 행이 선택된 경우에만 필드 생성
        if st.session_state.get('is_editing', False):  
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

            with st.form(key="update_form"):
                update_year, update_month, update_item_number, update_item_name, update_model, update_price, update_inventory, update_process = production_plan_form(
                    int(selected_row['날짜'].split('-')[0]),
                    int(selected_row['날짜'].split('-')[1]),
                    selected_row['품번'],
                    selected_row['품명'],
                    selected_row['모델'],
                    int(selected_row['단가']),
                    int(selected_row['생산계획']),
                    selected_row['공정'],
                    form_key="edit")

                if st.form_submit_button("저장"):
                    update_data = {
                        "year": update_year,
                        "month": update_month,
                        "item_number": update_item_number,
                        "item_name": update_item_name,
                        "inventory": update_inventory,
                        "model": update_model,
                        "price": update_price,
                        "process": update_process,
                    }
                    update_production_plan(prod_id, update_data)
                    st.session_state['is_editing'] = False
                    st.rerun()
        st.markdown("---")

        # 새로운 생산 계획 등록
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
            <div class="create-header">새로운 생산 계획 저장</div>
            """, 
            unsafe_allow_html=True
        )

        with st.form(key="create_form"):
            new_year, new_month, new_item_number, new_item_name, new_model, new_price, new_inventory, new_process = production_plan_form(form_key="create")
            if st.form_submit_button("저장"):
                new_data = {
                    "year": new_year,
                    "month": new_month,
                    "item_number": new_item_number,
                    "item_name": new_item_name,
                    "inventory": new_inventory,
                    "model": new_model,
                    "price": new_price,
                    "process": new_process,
                }
                create_production_plan(new_data)
                st.rerun()