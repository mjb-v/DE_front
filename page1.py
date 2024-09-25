# 생산계획관리

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

# 한글 컬럼명으로 변환
def translate_data(data):
    translation_dict = {
        "year": "년도",
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
        "inventory": "수량"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

# GET 전체 생산 계획 리스트
def get_all_plan(year: int):
    url = f"{API_URL}/plans/rate/{year}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

# GET 등록 페이지 테이블 데이터
def get_plan_register():
    response = requests.get(f"{API_URL}/plans/all/")
    if response.status_code == 200:
        data = response.json()
        df = translate_data(data)

        # '날짜' 컬럼 생성
        df['날짜'] = df.apply(lambda row: f"{int(row['년도'])}-{int(row['월']):02d}", axis=1)
        df = df.drop(columns=["년도", "월", "account_idx"])

        return df
    else:
        st.error("전체 생산 계획 리스트를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

# POST 생산 계획 저장
def create_production_plan(data):
    response = requests.post(f"{API_URL}/plans/", json=data)
    if response.status_code == 200:
        st.success("생산 계획이 성공적으로 저장되었습니다!")
        st.session_state['refresh_table'] = True  # 테이블 새로고침
    else:
        st.error("생산 계획 저장에 실패했습니다.")

# PUT 생산 계획 수정
def update_production_plan(plan_id, data):
    response = requests.put(f"{API_URL}/plans/{plan_id}", json=data)
    if response.status_code == 200:
        st.success("생산 계획이 성공적으로 수정되었습니다!")
        st.session_state['refresh_table'] = True
    else:
        st.error("생산 계획 수정에 실패했습니다.")

# DELETE 생산 계획 삭제
def delete_production_plan(plan_id):
    response = requests.delete(f"{API_URL}/plans/{plan_id}")
    if response.status_code == 200:
        st.success("생산 계획이 성공적으로 삭제되었습니다!")
        st.session_state['refresh_table'] = True
    else:
        st.error("생산 계획 삭제에 실패했습니다.")

# 생산 계획 등록/수정용 입력 필드 함수
def production_plan_form(item_number="", item_name="", model="", year=2024, month=1, inventory=0, price=0, form_key=""):
    # 각 입력 필드에 고유한 키 추가
    item_number = st.text_input("품번 입력", item_number, key=f"item_number_{form_key}")
    item_name = st.text_input("품명 입력", item_name, key=f"item_name_{form_key}")
    model = st.text_input("모델 입력", model, key=f"model_{form_key}")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        year = st.selectbox("년도 선택", options=list(range(2014, 2100)), index=year - 2014, key=f"year_{form_key}")
    with col2:
        month = st.selectbox("월 선택", options=list(range(1, 13)), index=month - 1, key=f"month_{form_key}")
    
    inventory = st.number_input("계획 수량", min_value=0, value=inventory, key=f"inventory_{form_key}")
    price = st.number_input("단가", min_value=0, value=price, key=f"price_{form_key}")
    
    return item_number, item_name, model, year, month, inventory, price

# ------------------------------------------------------------------------------------

def page1_view():
    st.title("생산 계획 관리")
    tab = st.sidebar.selectbox("", ["생산 계획 조회", "생산 계획 등록/수정"])

    # 1. 생산 계획 조회 페이지
    if tab == "생산 계획 조회":
        st.subheader("생산 계획")
        selected_year = st.sidebar.selectbox("년도 선택", list(range(2014, 2025)))
        plan_data = get_all_plan(selected_year)

        if plan_data:
            df = pd.DataFrame(plan_data)
            df = translate_data(df)
            df = df.drop(columns=["년도"])

            # 테이블 형식으로 변환 (month를 columns로, 나머지를 index로 변환, row 순서 정렬)
            df_pivot = df.set_index('월').T
            df_pivot.columns = [f"{month}월" for month in df_pivot.columns]
            row_order = ["사업계획", "사업실적", "사업달성율", "생산계획", "생산실적", "생산달성율"]
            df_pivot = df_pivot.reindex(row_order)

            # 테이블 출력
            st.subheader(f"{selected_year}년도 계획 및 실적 데이터")
            st.dataframe(df_pivot)

            # 그래프
            st.subheader(f"{selected_year}년 차트")

            # 월별로 사업 달성률과 생산 달성률 데이터 추출
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
        else:
            st.warning("계획 데이터가 없습니다.")

    # 2. 생산 계획 등록/수정 페이지
    elif tab == "생산 계획 등록/수정":
        st.subheader("생산 계획 등록/수정")

        if 'refresh_table' not in st.session_state:
            st.session_state['refresh_table'] = False

        if st.session_state['refresh_table']:
            reg_data = get_plan_register()  # 테이블 데이터 새로 가져옴
            st.session_state['refresh_table'] = False  # 새로고침 후 플래그 초기화
        else:
            reg_data = st.session_state.get('reg_data', get_plan_register())  # 처음에는 데이터를 불러옴

        if not reg_data.empty:
            st.dataframe(reg_data[['날짜', '품번', '품명', '모델', '수량', '단가']])

            # 수정/삭제할 행의 인덱스를 선택할 selectbox
            col1, col2 = st.columns([2, 1])
            with col1:
                selected_index = st.selectbox("수정/삭제할 행의 인덱스", reg_data.index, key="select_index", label_visibility='collapsed')

            with col2:
                # 수정/삭제 버튼을 가깝게 배치
                if st.button("수정", key="edit_button"):
                    selected_plan = reg_data.loc[selected_index]
                    st.session_state['edit_row_id'] = selected_plan['id']

                if st.button("삭제", key="delete_button"):
                    selected_plan = reg_data.loc[selected_index]
                    delete_production_plan(selected_plan['id'])

            # 수정할 행이 선택된 경우에만 수정 폼을 보여줌
            if 'edit_row_id' in st.session_state and st.session_state['edit_row_id'] == reg_data.loc[selected_index]['id']:
                selected_plan = reg_data.loc[selected_index]
                st.subheader(f"수정할 항목: {selected_plan['품번']} - {selected_plan['품명']}")

                # 수정할 값을 입력할 수 있는 폼 생성
                with st.form(key="edit_form"):
                    update_item_number, update_item_name, update_model, update_year, update_month, update_inventory, update_price = production_plan_form(
                        selected_plan['품번'], selected_plan['품명'], selected_plan['모델'],
                        int(selected_plan['날짜'].split('-')[0]), int(selected_plan['날짜'].split('-')[1]),
                        int(selected_plan['수량']), int(selected_plan['단가']),
                        form_key="edit")

                    # 수정된 내용을 저장하는 버튼
                    if st.form_submit_button("저장"):
                        updated_data = {
                            "year": update_year,
                            "month": update_month,
                            "item_number": update_item_number,
                            "item_name": update_item_name,
                            "inventory": update_inventory,
                            "model": update_model,
                            "price": update_price
                        }
                        update_production_plan(st.session_state['edit_row_id'], updated_data)
                        st.session_state['edit_row_id'] = None  # 수정 완료 후 초기화
            else:
                st.info("수정/삭제할 행을 선택하고 버튼을 클릭하세요.")
        else:
            st.warning("등록된 생산 계획이 없습니다.")

        # 새로운 생산 계획 등록
        st.subheader("새로운 생산 계획 등록")
        new_item_number, new_item_name, new_model, new_year, new_month, new_inventory, new_price = production_plan_form(form_key="new")

        # 저장 버튼을 클릭했을 때 POST 요청
        if st.button("저장"):
            new_data = {
                "year": new_year,
                "month": new_month,
                "item_number": new_item_number,
                "item_name": new_item_name,
                "inventory": new_inventory,
                "model": new_model,
                "price": new_price
            }
            create_production_plan(new_data)