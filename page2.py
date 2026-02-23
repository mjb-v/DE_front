import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
from datetime import datetime
from natsort import natsorted
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")

# 한글 컬럼명으로 변환
def translate_data(data):
    translation_dict = {
        "date": "날짜",
        "item_number": "품번",
        "item_name": "품명",
        "line": "라인",
        "operator": "작업자",
        "model": "모델",
        "target_quantity": "목표수량",
        "produced_quantity": "생산수량",
        "production_efficiency": "생산효율",
        "operating_time": "가동시간",
        "non_operating_time": "비가동시간",
        "line_efficiency": "설비효율"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

def get_production_data(start_date, end_date, operator, item_number, item_name):
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'operator': operator,
        'item_number': item_number,
        'item_name': item_name
    }
    response = requests.get(f"{API_URL}/productions/days/", params=params)
    if response.status_code == 200:
        return translate_data(response.json())
    else:
        st.error("데이터를 가져오는 데 실패했습니다.")
        return pd.DataFrame()

# ------------------------------------------------------------------------------------------------
def page2_view():
    st.markdown("<h2 style='text-align: left;'>📈 생산 실적 관리</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)

    today = datetime.today()
    last_day = calendar.monthrange(today.year, today.month)[1]

    # -------------------------------------------------------------
    # 🔍 검색/조회
    # -------------------------------------------------------------
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

    with st.form("search_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input('시작 날짜', value=datetime(today.year, today.month, 1))
        with col2:
            end_date = st.date_input('종료 날짜', value=datetime(today.year, today.month, last_day))
        with col3:
            operator = st.text_input('작업자 이름 입력')
        col4, col5 = st.columns(2)
        with col4:
            item_number = st.text_input('품번 입력')
        with col5:
            item_name = st.text_input('품명 입력')
            
        submit_btn = st.form_submit_button("조회하기", use_container_width=True)

    # -------------------------------------------------------------
    # ⚙️ 데이터 불러오기 및 세션 저장
    # -------------------------------------------------------------
    if submit_btn or 'df' not in st.session_state:
        df = get_production_data(start_date, end_date, operator, item_number, item_name)
        if not df.empty:
            selected_columns = ["날짜", "품번", "품명", "라인", "작업자", "모델", "생산수량", "생산효율", "가동시간", "설비효율"]
            df = df[selected_columns]
            st.session_state['df'] = df
        else:
            if submit_btn:
                st.warning("검색 결과가 없습니다.")
            if 'df' in st.session_state:
                del st.session_state['df']

    # -------------------------------------------------------------
    # 📊 테이블 및 차트 렌더링
    # -------------------------------------------------------------
    if 'df' in st.session_state:
        df = st.session_state['df']
        
        st.markdown(f"총 **{len(df)}**건의 실적이 조회되었습니다.")
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        
        lines = natsorted(df['라인'].unique().tolist())
        num_columns = 4

        # < 생산효율 차트  >
        on_production = st.toggle("평균 생산효율 보기 (OFF 시 박스플롯)", value=True)

        selected_lines_efficiency = []
        cols = st.columns(num_columns)
        default_checked_lines = ["Line1", "Line2", "Line3"]

        for i, line in enumerate(lines):
            col = cols[i % num_columns]
            checked = line in default_checked_lines
            if col.checkbox(f'{line}', value=checked, key=f"line_production_{line}"):
                selected_lines_efficiency.append(line)

        if on_production:
            st.subheader('라인별 평균 생산효율')
            filtered_data_efficiency = df[df['라인'].isin(selected_lines_efficiency)]
            grouped_data_efficiency = (
                filtered_data_efficiency.groupby(['날짜', '라인'], as_index=False)
                .agg({'생산효율': 'mean'})
            )
            fig_efficiency = px.line(grouped_data_efficiency, x='날짜', y='생산효율', color='라인', markers=True)
            fig_efficiency.update_xaxes(tickformat='%b %d')
            st.plotly_chart(fig_efficiency, use_container_width=True)
        else:
            st.subheader('라인별 생산효율')
            filtered_data_production = df[df['라인'].isin(selected_lines_efficiency)]
            fig_production = px.box(filtered_data_production, x='날짜', y='생산효율', color='라인')
            fig_production.update_xaxes(tickformat='%b %d')
            st.plotly_chart(fig_production, use_container_width=True)

        # < 설비효율 차트 >
        st.markdown("<br>", unsafe_allow_html=True)
        on_equipment = st.toggle("평균 설비효율 보기 (OFF 시 박스플롯)", value=True)

        selected_lines_equipment = []
        cols_equipment = st.columns(num_columns)

        for i, line in enumerate(lines):
            col = cols_equipment[i % num_columns]
            checked = line in default_checked_lines
            if col.checkbox(f'{line}', value=checked, key=f"line_equipment_{line}"):
                selected_lines_equipment.append(line)

        if on_equipment:
            st.subheader('라인별 평균 설비효율')
            filtered_data_equipment = df[df['라인'].isin(selected_lines_equipment)]
            grouped_data_equipment = (
                filtered_data_equipment.groupby(['날짜', '라인'], as_index=False)
                .agg({'설비효율': 'mean'})
            )
            fig_equipment = px.line(grouped_data_equipment, x='날짜', y='설비효율', color='라인', markers=True)
            fig_equipment.update_xaxes(tickformat='%b %d')
            st.plotly_chart(fig_equipment, use_container_width=True)
        else:
            st.subheader('라인별 설비효율')
            filtered_data_equipment = df[df['라인'].isin(selected_lines_equipment)]
            fig_equipment_box = px.box(filtered_data_equipment, x='날짜', y='설비효율', color='라인')
            fig_equipment_box.update_xaxes(tickformat='%b %d')
            st.plotly_chart(fig_equipment_box, use_container_width=True)

    st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 2px 0;'>", unsafe_allow_html=True)
    st.markdown("**Note:** 그래프는 각 날짜의 라인별 평균 생산효율과 설비효율을 계산한 값입니다.")