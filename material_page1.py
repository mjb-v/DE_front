# 자재관리 1. 자재계획관리

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
        "business_amount": "사업실적",
        "business_achievement_rate": "사업달성율",
        "item_number": "품번",
        "item_name": "품명",
        "client_code": "거래처코드",
        "previous_amount": "전월실적",
        "current_amount": "당월실적",
        "growth_rate": "증감율",
        "client": "거래처명", # (dropdown: (주)금성오토텍, 
        "model": "모델구분", # (dropdown: 가정, 건조기, 세탁기, 식기세척기, 에어컨, 중장비)
        "item_category": "품목구분", # (dropdown: 원재료, 부재료, 재공품, 제품, 반제품)
        "process": "공정구분", # (drodown: 검사/조립, 사출)
        "quantity": "계획수량"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

# 1-1. 위 - 전체 플랜 GET
def get_all_plan(year: int):
    response = requests.get(f"{API_URL}/material/rate/{year}")
    if response.status_code == 200:
        data = response.json()
        df = translate_data(data)
        df = df.drop(columns=["년도"])
        df_pivot = df.set_index('월').T
        df_pivot.columns = [f"{month}월" for month in df_pivot.columns]
        row_order = ["사업계획", "사업실적", "사업달성율"]
        df_pivot = df_pivot.reindex(row_order)
        return df, df_pivot
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

# 1-2. 아래 - 당월 플랜
def get_material_all_plan(year: int, month: int):
    response = requests.get(f"{API_URL}/materials/rates/{year},{month}")
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

# 2-1. 등록 페이지 전체 테이블 보여주기 GET
def get_plan_register():
    response = requests.get(f"{API_URL}/materials/all/")
    if response.status_code == 200:
        data = response.json()
        return translate_data(data)
    else:
        st.error("전체 자재관리 계획 리스트를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

# 2-2. 자재관리계획 저장 POST
def create_material_plan(data):
    response = requests.post(f"{API_URL}/materials/", json=data)
    if response.status_code == 200:
        st.success("자재관리 계획이 성공적으로 저장되었습니다!")
    else:
        st.error("자재관리 계획 저장에 실패했습니다.")

# 2-3. 자재관리계획 수정 PUT
def update_material_plan(material_id, data):
    response = requests.put(f"{API_URL}/materials/{material_id}", json=data)
    if response.status_code == 200:
        st.success("자재관리 계획이 성공적으로 수정되었습니다!")
    else:
        st.error("자재관리 계획 수정에 실패했습니다.")

# 2-4. 자재관리계획 삭제 DELETE
def delete_material_plan(material_id):
    response = requests.delete(f"{API_URL}/materials/{material_id}")
    if response.status_code == 200:
        st.success("자재관리 계획이 성공적으로 삭제되었습니다!")
    else:
        st.error("자재관리 계획 삭제에 실패했습니다.")

# 2. 자재관리계획 입력 필드
def material_plan_form(date=None, client = "", item_number="", item_name="", item_category="원재료", model="가전", process="사출", quantity=0, form_key=""):
    category_options = ["원재료", "부재료", "재공품", "제품", "반제품"]
    model_options = ["가전", "건조기", "세탁기", "식기세척기", "에어컨", "중장비", "포장박스", "LX2PE", "GEN3.5", "MX5"]
    process_options = ["검사/조립", "사출"]

    if date is None:
        date = datetime.today().date()
    selected_date = st.date_input("날짜 선택", value=date, key=f"date_{form_key}")

    client = st.selectbox("거래처명", options=company_names, index=company_names.index(client) if client in company_names else 0, key=f"company_names_{form_key}")
    item_number = st.text_input("품번 입력", item_number, key=f"item_number_{form_key}")
    item_name = st.text_input("품명 입력", item_name, key=f"item_name_{form_key}")
    item_category = st.selectbox("품목 선택", options=category_options, index=category_options.index(item_category), key=f"item_category_{form_key}")
    model = st.selectbox("모델 선택", options=model_options, index=model_options.index(model), key=f"model_{form_key}")
    process = st.selectbox("공정 구분", options=process_options, index=process_options.index(process), key=f"process_{form_key}")
    quantity = st.number_input("계획 수량", min_value=0, value=quantity, key=f"quantity_{form_key}")

    return client, item_number, item_name, item_category, model, selected_date, quantity, process

# ----------------------------------------------------------------
def material_page1_view():
    st.markdown("<h2 style='text-align: left;'>📝 자재 계획 관리</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)

    tab = st.sidebar.radio(" ", ["자재 계획 조회", "자재 계획 등록/수정"])

    if tab == "자재 계획 조회":
        st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>필터 설정</div>", unsafe_allow_html=True)

        current_year = datetime.today().year
        current_month = datetime.today().month
        selected_year = st.sidebar.selectbox("년도 선택", list(range(2014, 2025)), index=list(range(2014, 2025)).index(current_year))
        selected_month = st.sidebar.selectbox("월 선택", list(range(1, 13)), index=list(range(1, 13)).index(current_month))

        df, df1 = get_all_plan(selected_year)
        st.subheader(f"{selected_year}년도 계획 및 실적 데이터")
        st.dataframe(df1)

        df2 = get_material_all_plan(selected_year, selected_month)
        if df2.empty:
            pass
        else:
            st.subheader(f"{selected_year}년 {selected_month}월")
            df2 = df2.drop(columns=['년도','월'])
            st.dataframe(df2)

        # 그래프 --> 거래처 선택 & 해당 년도의 증감율만 보여주기
        business_achievement_rates = df["사업달성율"]
        months = df["월"].apply(lambda x: f"{x}월")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(months, business_achievement_rates, width=0.4, label='사업 달성률', align='center', color='#ff9999')
        ax.set_ylim(0, 100)
        ax.set_ylabel('달성률 (%)')
        ax.set_title(f"{selected_year}년 월별 사업 달성률")
        ax.legend()
        st.pyplot(fig)

    elif tab == "자재 계획 등록/수정":
        # 전체 데이터 가져오기 및 테이블 표시
        df = get_plan_register()
        if not df.empty:
            df_display = df.drop(columns=["id", "account_idx"])
            st.dataframe(df_display)

        # 수정/삭제할 행 선택 및 버튼 배치
        st.subheader("수정/삭제")
        col1, col2 = st.columns([2, 1])

        with col1:
            selected_index = st.selectbox("수정/삭제할 줄의 번호 선택", df.index, key="select_index")
            
        with col2:
            selected_row = df.loc[selected_index]
            material_id = selected_row["id"]

            # 수정 버튼
            if st.button("수정", key="edit_button"):
                st.session_state['is_editing'] = True

            # 삭제 버튼
            if st.button("삭제", key="delete_button"):
                delete_material_plan(material_id)
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
                client, item_number, item_name, item_category, model, selected_date, quantity, process = material_plan_form(
                    client=selected_row["거래처명"],
                    item_number=selected_row["품번"],
                    item_name=selected_row["품명"],
                    item_category=selected_row["품목구분"],
                    model=selected_row["모델구분"],
                    date=pd.to_datetime(selected_row["날짜"]).date(),
                    quantity=selected_row["계획수량"],
                    process=selected_row["공정구분"],
                    form_key="update")

                if st.form_submit_button("저장"):
                    update_data = {
                        "client": client,
                        "item_number": item_number,
                        "item_name": item_name,
                        "item_category": item_category,
                        "model": model,
                        "date": selected_date.strftime("%Y-%m-%d"),
                        "quantity": quantity,
                        "process": process
                    }
                    update_material_plan(material_id, update_data)
                    st.session_state['is_editing'] = False
                    st.rerun()
        st.markdown("---")

        # '새로운 계획 저장'
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
            <div class="create-header">새로운 자재관리 계획 저장</div>
            """, 
            unsafe_allow_html=True
        )

        with st.form(key="create_form"):
            client, item_number, item_name, item_category, model, selected_date, quantity, process = material_plan_form(form_key="create")
            if st.form_submit_button("저장"):
                new_data = {
                    "client": client,
                    "item_number": item_number,
                    "item_name": item_name,
                    "item_category": item_category,
                    "model": model,
                    "date": selected_date.strftime("%Y-%m-%d"),
                    "quantity": quantity,
                    "process": process
                }
                create_material_plan(new_data)
                st.rerun()
