import streamlit as st
from matplotlib import font_manager, rc
from page1 import page1_view
from page2 import page2_view
from page3 import page3_view
from page4 import page4_view
from material_page1 import material_page1_view
from material_page2 import material_page2_view

# 페이지 설정
st.set_page_config(layout="wide")

# 한글 폰트 설정
font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

# 선택할 수 있는 회사 리스트 샘플
companies = {
    "뉴텍SDS": {"logo": "newtech_logo.png", "connected": "연결됨"},
    "Company A": {"logo": "logo_a.png", "connected": "연결됨"},
    "Company B": {"logo": "logo_b.png", "connected": "연결됨"}
}

# 기업 선택
st.sidebar.markdown("""
    <style>
        .custom-title {
            font-size: 30px;
            margin-bottom: -55px;  /* 간격을 줄이기 위한 설정 */
        }
    </style>
    <h1 class='custom-title'>기업 선택</h1>
    """, unsafe_allow_html=True)
selected_company = st.sidebar.selectbox(" ", list(companies.keys()))
company_info = companies[selected_company]

# 사이드바 상단에 회사명, 로고, 연결 상태 표시
st.sidebar.image(company_info['logo'], width=100)
st.sidebar.write(f"상태: {company_info['connected']}")

# 탭 선택 (수평 배치)
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "생산 관리"

# HTML로는 아무리해도 배치 적용이 안되므로 임의로 다중 컬럼 사용
col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)
with col1:
    if st.button("생산 관리"):
        st.session_state.selected_tab = "생산 관리"
with col2:
    if st.button("자재 관리"):
        st.session_state.selected_tab = "자재 관리"
selected_tab = st.session_state.selected_tab

# 선택된 탭에 따라 사이드바 메뉴 변경
if selected_tab == "생산 관리":
    st.sidebar.markdown("""
        <style>
            .custom-title {
                font-size: 30px;
                margin-bottom: -55px;
            }
        </style>
        <h3 class='custom-title'>생산 관리</h3>
        """, unsafe_allow_html=True)
    
    # 생산 관리 드롭다운 메뉴
    page = st.sidebar.selectbox('', ("생산계획관리", "생산실적관리", "생산현황관리", "재고관리"))

    # 선택한 페이지에 따라 해당 함수 호출
    if page == "생산계획관리":
        page1_view()
    elif page == "생산실적관리":
        page2_view()
    elif page == "생산현황관리":
        page3_view()
    elif page == "재고관리":
        page4_view()

elif selected_tab == "자재 관리":
    st.sidebar.markdown("""
        <style>
            .custom-title {
                font-size: 30px;
                margin-bottom: -55px;
            }
        </style>
        <h3 class='custom-title'>자재 관리</h3>
        """, unsafe_allow_html=True)
    
    # 자재 관리 드롭다운 메뉴
    page = st.sidebar.selectbox('', ("자재계획관리", "자재입고관리"))

    # 선택한 페이지에 따라 해당 함수 호출
    if page == "자재계획관리":
        material_page1_view()
    elif page == "자재입고관리":
        material_page2_view()
