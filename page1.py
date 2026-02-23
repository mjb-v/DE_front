import plotly.graph_objects as go
from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import time
from utils import get_sidebar_filters

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
        "current_inventory": "현재고",
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
def production_plan_form(year=None, month=None, item_number="", item_name="", model="가전", price=0, inventory=0, process="사출", form_key=""):
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
        with st.spinner("AI가 실시간 재고와 수요예측 데이터를 분석 중입니다..."):
            today = datetime.today()
            inv_df = pd.DataFrame()

            try:
                inv_res = requests.get(f"{API_URL}/inventories/month/", params={"year": today.year, "month": today.month})
                if inv_res.status_code == 200 and inv_res.json():
                    inv_df = pd.DataFrame(inv_res.json())
                    inv_df = inv_df[['item_number', 'item_name', 'current_quantity']].rename(columns={
                        'item_number': '품번', 'item_name': '품명', 'current_quantity': '현재고'
                    })
                    inv_df = inv_df.groupby(['품번', '품명'], as_index=False)['현재고'].sum()
                    inv_df = inv_df[inv_df['현재고'] > 0]
            except:
                pass

            total_pred_order = 0
            total_pred_safety = 0
            try:
                pred_payload = {
                    "daily_out": 100, "capa": 150, "delivery_date": today.strftime("%Y-%m-%d"),
                    "stock_finished": 500, "stock_wip": 200, "stock_part1": 1000,
                    "order_vol": 3000, "lead_time_part1": 14, "method": "ARIMA", "forecast_months": 1
                }
                pred_res = requests.post(f"{API_URL}/predictions/mass_production", json=pred_payload)
                if pred_res.status_code == 200:
                    pred_data = pred_res.json()
                    pred_order_dict = pred_data.get("order_volume", {}).get("prediction", {})
                    pred_safe_dict = pred_data.get("safety_stock", {}).get("prediction", {})
                    
                    if pred_order_dict:
                        total_pred_order = list(pred_order_dict.values())[0]
                        total_pred_safety = list(pred_safe_dict.values())[0]
            except:
                pass

            warning_data = pd.DataFrame()
            if not inv_df.empty and total_pred_order > 0:
                total_inventory = inv_df['현재고'].sum()
                inv_df['재고점유율'] = inv_df['현재고'] / total_inventory
                inv_df['다음달_예상수요(AI)'] = (total_pred_order * inv_df['재고점유율']).astype(int)
                inv_df['안전재고'] = (total_pred_safety * inv_df['재고점유율']).astype(int)
                inv_df['부족_수량'] = (inv_df['다음달_예상수요(AI)'] + inv_df['안전재고']) - inv_df['현재고']
                warning_data = inv_df[inv_df['부족_수량'] > 0].sort_values(by="부족_수량", ascending=False)

        if not warning_data.empty:
            st.markdown(
                """
                <style>
                .alert-box { background-color: #fff1f0; border-left: 6px solid #ff4d4f; padding: 20px; border-radius: 5px; margin-bottom: 25px; }
                .alert-title { color: #cf1322; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; margin-top: 0; }
                </style>
                <div class="alert-box">
                    <p class="alert-title">AI 재고 모니터링</p>
                    <p style="margin:0; font-size: 0.95rem; color:#555;">다음 달 수요예측 대비 <strong style="color:#cf1322;">안전 재고가 부족한 품목</strong>입니다.</p>
                </div>
                """, unsafe_allow_html=True
            )
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.dataframe(
                    warning_data.drop(columns=['재고점유율']).style.format({
                        "현재고": "{:,.0f} 개", "다음달_예상수요(AI)": "{:,.0f} 개", 
                        "안전재고": "{:,.0f} 개", "부족_수량": "{:,.0f} 개"
                    }).background_gradient(subset=['부족_수량'], cmap='Reds'),
                    use_container_width=True
                )
            with col2:
                st.info("💡 **산출 공식**\n\n부족 수량 = (예상수요 + 안전재고) - 현재고")
                
        elif inv_df.empty:
            st.warning("⚠️ 백엔드 API에서 데이터를 가져오는 데 실패했습니다.")
        else:
            st.success("✅ 현재 모든 품목의 재고가 충분합니다!")

        st.markdown("<hr style='border:1px dashed #E0E0E0; margin: 25px 0;'>", unsafe_allow_html=True)
        # -------------------------------------------------------------------
        st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>필터 설정</div>", unsafe_allow_html=True)

        selected_year, selected_month = get_sidebar_filters()
        df = get_all_plan(selected_year)
        df1 = df.set_index('월').T
        df1.columns = [f"{month}월" for month in df1.columns]
        row_order = ["사업계획", "사업실적", "사업달성율", "생산계획", "생산실적", "생산달성율"]
        df1 = df1.reindex(row_order)
        st.subheader(f"{selected_year}년도 계획 및 실적 데이터")
        st.dataframe(df1.style.format("{:,.0f}"))

        df2 = get_monthly_plan(selected_year, selected_month)
        if df2.empty:
            pass
        else:
            st.subheader(f"{selected_year}년 {selected_month}월")
            df2 = df2.drop(columns=['연도','월'])
            st.dataframe(df2.style.format(thousands=","))

        # 그래프
        st.markdown("---")
        
        df_chart = df.copy()
        df_chart['월_숫자'] = pd.to_numeric(df_chart['월'], errors='coerce').fillna(0).astype(int)
        df_chart = df_chart.sort_values('월_숫자')

        months = df_chart['월_숫자'].apply(lambda x: f"{x}월").tolist()
        business_rates = pd.to_numeric(df_chart['사업달성율'], errors='coerce').fillna(0).tolist()
        production_rates = pd.to_numeric(df_chart['생산달성율'], errors='coerce').fillna(0).tolist()

        if sum(business_rates) == 0 and sum(production_rates) == 0:
            st.info("📌 현재 시스템에 등록된 계획 수량이 없어 달성률이 0%로 표시됩니다.")
            
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=months, 
            y=business_rates,
            name='사업 달성율',
            marker_color='#FF9999',
            text=[f"{val:.1f}%" for val in business_rates],
            textposition='outside'
        ))
        fig.add_trace(go.Bar(
            x=months, 
            y=production_rates,
            name='생산 달성율',
            marker_color='#66B2FF',
            text=[f"{val:.1f}%" for val in production_rates],
            textposition='outside'
        ))
        max_val = max(max(business_rates) if business_rates else 0, 
                      max(production_rates) if production_rates else 0)
        
        fig.update_layout(
            title="📈 월별 사업 및 생산 달성률 추이",
            title_font_size=20,
            barmode='group',
            xaxis_title="월",
            yaxis_title="달성률 (%)",
            yaxis=dict(range=[0, max_val + 15]),
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, b=20, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

    # 2. 생산 계획 등록/수정 페이지
    elif tab == "생산 계획 등록/수정":
        df = get_plan_register()
        if not df.empty:
            df = df.sort_values(by='날짜', ascending=False).reset_index(drop=True)

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

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                date_options = ["전체"] + sorted(list(df['날짜'].unique()), reverse=True)
                search_date = st.selectbox("등록연월", options=date_options)
            with col2:
                process_options = ["전체"] + sorted(list(df['공정'].dropna().unique()))
                search_process = st.selectbox("공정 (라인선택)", options=process_options)
            with col3:
                search_item_no = st.text_input("품번 검색")
            with col4:
                search_item_name = st.text_input("품명 검색")
            filtered_df = df.copy()
            
            if search_date != "전체":
                filtered_df = filtered_df[filtered_df['날짜'] == search_date]
            if search_process != "전체":
                filtered_df = filtered_df[filtered_df['공정'] == search_process]
            if search_item_no:
                filtered_df = filtered_df[filtered_df['품번'].str.contains(search_item_no, na=False, case=False)]
            if search_item_name:
                filtered_df = filtered_df[filtered_df['품명'].str.contains(search_item_name, na=False, case=False)]

            st.markdown(f"총 **{len(filtered_df)}**건이 검색되었습니다.")
            df_display = filtered_df[['날짜', '품번', '품명', '모델', '단가', '현재고', '생산계획', '공정']]
            st.dataframe(df_display.style.format({"단가": "{:,.0f}", "현재고": "{:,.0f}", "생산계획": "{:,.0f}"}), use_container_width=True)

        st.subheader("수정/삭제")
        col1, col2 = st.columns([2, 1])

        with col1:
            if not filtered_df.empty:
                selected_index = st.selectbox("수정/삭제할 줄의 번호 선택", filtered_df.index, key="select_index")
            else:
                st.info("검색 결과가 없어 수정할 항목을 선택할 수 없습니다.")
                selected_index = None

        with col2:
            if selected_index is not None:
                selected_row = df.loc[selected_index]
                prod_id = selected_row["plan_idx"]

                if st.button("수정", key="edit_button"):
                    st.session_state['is_editing'] = True

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