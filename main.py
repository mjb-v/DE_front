import streamlit as st
from matplotlib import font_manager, rc
from page1 import page1_view
from page2 import page2_view
from page3 import page3_view
from page4 import page4_view
from material_page1 import material_page1_view
from material_page2 import material_page2_view
from material_page3 import material_page3_view
from material_page4 import material_page4_view
from prediction import prediction_view

# 페이지 설정
st.set_page_config(
    page_title="제조 혁신",
    page_icon="🌟",
    layout="wide"
)

# 한글 폰트 설정
font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

# 선택할 수 있는 회사 리스트 샘플
companies = {
    "뉴텍SDS": {"logo": "images/newtech_logo.png", "connected": "연결됨"},
    "Company A": {"logo": "images/logo_a.jpg", "connected": "연결됨"},
    "Company B": {"logo": "images/logo_b.jpg", "connected": "연결됨"}
}

# 사이드바 커스텀 스타일
st.sidebar.markdown("""
    <style>
        .sidebar-section {
            margin-bottom: 30px;
        }
        .sidebar-title {
            font-size: 26px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }
        .sidebar-subtitle {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }
        .sidebar-company-logo {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 150px;
            padding-bottom: 10px;
        }
        .sidebar-company-status {
            font-size: 18px;
            font-weight: 600;
            color: #4CAF50;
            text-align: left;
        }
        .stButton {
            margin: 0 10px;
        }
        .sidebar-selectbox {
            font-size: 16px;
            margin-bottom: 10px;
        }
        .custom-line {
            border-top: 1px solid #ccc;
            margin: 2px 0;
        }
        .divider {
            border-top: 2px solid #e6e6e6;
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

# 기업 선택 섹션
st.sidebar.markdown("<div class='sidebar-section sidebar-title'>기업 선택</div>", unsafe_allow_html=True)
selected_company = st.sidebar.selectbox(" ", list(companies.keys()))
company_info = companies[selected_company]

# 로고와 상태 표시
st.sidebar.image(company_info['logo'], width=150, use_column_width=True, caption=None, output_format='auto')
st.sidebar.markdown(f"<div class='sidebar-company-status'>상태: {company_info['connected']}</div>", unsafe_allow_html=True)

# 구분선 추가
st.sidebar.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# 기본 탭 섹션
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "생산 관리"

# 탭 버튼 배치 (간격 조정을 위해 빈 컬럼 추가)
col1, col2, col3 = st.sidebar.columns([1, 1, 1])
with col1:
    if st.button("생산 관리"):
        st.session_state.selected_tab = "생산 관리"
with col2:
    if st.button("자재 관리"):
        st.session_state.selected_tab = "자재 관리"
with col3:
    if st.button("수요 예측"):
        st.session_state.selected_tab = "수요 예측"

selected_tab = st.session_state.selected_tab

# 선택된 탭에 따라 사이드바 메뉴 변경
if selected_tab == "생산 관리":
    st.sidebar.markdown("<div class='sidebar-section sidebar-title stButton'>생산 관리</div>", unsafe_allow_html=True)
    page = st.sidebar.selectbox(' ', ("생산계획관리", "생산실적관리", "생산현황관리", "재고관리"))

    if page == "생산계획관리":
        page1_view()
    elif page == "생산실적관리":
        page2_view()
    elif page == "생산현황관리":
        st.sidebar.empty()
        page3_view()
    elif page == "재고관리":
        page4_view()

elif selected_tab == "자재 관리":
    st.sidebar.markdown("<div class='sidebar-section sidebar-title stButton'>자재 관리</div>", unsafe_allow_html=True)
    page = st.sidebar.selectbox(' ', ("자재계획관리", "자재입고관리", "재고관리", "LOT재고관리"))

    if page == "자재계획관리":
        material_page1_view()
    elif page == "자재입고관리":
        material_page2_view()
    elif page == "재고관리":
        material_page3_view()
    elif page == "LOT재고관리":
        material_page4_view()

elif selected_tab == "수요 예측":
    st.sidebar.markdown("<div class='sidebar-section sidebar-title stButton'>수요 예측</div>", unsafe_allow_html=True)
    prediction_view()

