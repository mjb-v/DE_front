import pandas as pd
import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from matplotlib import font_manager, rc
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from utils import get_sidebar_filters

font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

# FastAPI URL
load_dotenv()
API_URL = os.getenv("API_URL")

# 1. 생산 실적
def get_prod_plan(year: int):
    response = requests.get(f"{API_URL}/plans/rate/{year}")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data).rename(columns={"year":"년도", "month":"월", "business_amount":"생산 실적"})
        df["생산 실적"] = df["생산 실적"].round().astype(int).apply(lambda x: f"{x:,}")
        df["년도"] = df["년도"].astype(str)
        df["날짜"] = df.apply(lambda x: f"{x['년도']}-{int(x['월']):02d}", axis=1)
        df = df[["날짜", "생산 실적"]].set_index("날짜").transpose()
        return df
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

# 2. 자재 실적
def get_inven_plan(year: int):
    response = requests.get(f"{API_URL}/material/rate/{year}")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data).rename(columns={"year":"년도", "month":"월", "business_amount":"매입 실적"})
        df["매입 실적"] = df["매입 실적"].round().astype(int).apply(lambda x: f"{x:,}")
        df["년도"] = df["년도"].astype(str)
        df["날짜"] = df.apply(lambda x: f"{x['년도']}-{int(x['월']):02d}", axis=1)
        df = df[["날짜", "매입 실적"]].set_index("날짜").transpose()
        return df
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

def highlight_prod(row):
    return ['background-color: #E3F2FD']*len(row)
def highlight_inven(row):
    return ['background-color: #FFF8E1']*len(row)

# 5 --- [API 호출 함수들] ---
def get_exchange_rate(api_key):
    for i in range(5):
        target_date = (datetime.today() - timedelta(days=i)).strftime('%Y%m%d')
        url = f"https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={api_key}&searchdate={target_date}&data=AP01"
        
        try:
            requests.packages.urllib3.disable_warnings() 
            response = requests.get(url, verify=False)
            data = response.json()
            
            if data: 
                for item in data:
                    if item.get('cur_unit') == 'USD':
                        return {"rate": f"{item.get('deal_bas_r')} 원", "date": target_date}
        except Exception as e:
            continue
            
    return {"rate": "조회 불가", "date": "-"}

def get_trade_data(api_key):
    today = datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_month_date = first_day_of_this_month - timedelta(days=1)
    target_yymm = last_month_date.strftime('%Y%m')
    
    url = f"https://apis.data.go.kr/1220000/Newtrade/getNewtradeList?serviceKey={api_key}&strtYymm={target_yymm}&endYymm={target_yymm}"
    
    try:
        response = requests.get(url)
        root = ET.fromstring(response.text)
        result_code = root.find('.//resultCode')
        
        if result_code is not None and result_code.text == '00':
            item = root.find('.//item')
            
            if item is not None:
                exp_dlr = int(item.find('expDlr').text) // 1000000
                imp_dlr = int(item.find('impDlr').text) // 1000000
                bal_payments = int(item.find('balPayments').text) // 1000000
                year_month = item.find('year').text 
                
                return {
                    "status": "success",
                    "month": year_month,
                    "exp": f"{exp_dlr:,}",
                    "imp": f"{imp_dlr:,}",
                    "bal": f"{bal_payments:,}"
                }
        return {"status": "error", "msg": "XML 구조 변경 또는 데이터 없음"}
            
    except Exception as e:
        return {"status": "error", "msg": str(e)}

# 6. --- [그래프 공통 함수] ---
def draw_prediction_chart(df_history, df_pred, title, y_axis_title, hist_color, pred_color):
    fig = go.Figure()
    
    # 과거 실적
    if df_history is not None and not df_history.empty:
        fig.add_trace(go.Scatter(
            x=df_history.columns, y=df_history.iloc[0],
            mode='lines+markers', name='현재 실적',
            line=dict(color=hist_color, width=3),
            marker=dict(color=hist_color, size=8)
        ))

    # 미래 예측
    if df_pred is not None and not df_pred.empty:
        pred_df_plot = df_pred.copy()

        if df_history is not None and not df_history.empty:
            last_value = df_history.iloc[0, -1]
            last_date = df_history.columns[-1]
            pred_df_plot.insert(0, last_date, last_value)         
        fig.add_trace(go.Scatter(
            x=pred_df_plot.columns, y=pred_df_plot.iloc[0],
            mode='lines+markers', name='예측 데이터',
            line=dict(color=pred_color, dash='dash', width=3),
            marker=dict(color=pred_color, size=8)
        ))
    fig.update_layout(
        title=f"📈 {title}",
        xaxis_title="기간(월)",
        yaxis_title=y_axis_title,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        hovermode="x",
        font=dict(family="NanumGothic, sans-serif", size=14),
        title_font=dict(size=20, color="black"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

# 7. --- [양산 단계 화면 구성] ---
def mass_production_view():
    st.markdown("<h2 style='text-align: left; color: #007BFF;'>⚙️ 양산 단계 수요 예측</h2>", unsafe_allow_html=True)

    EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")
    TRADE_API_KEY = os.getenv("TRADE_API_KEY")
    current_exchange = get_exchange_rate(EXCHANGE_API_KEY)
    trade_data = get_trade_data(TRADE_API_KEY)

    st.markdown("#### 🌍 경제 지표")
    st.caption("출처: 한국수출입은행 (www.koreaexim.go.kr), 공공데이터포털 (www.data.go.kr)")
    
    col1, col2, col3, col4 = st.columns(4)
    target_date_formatted = current_exchange['date']
    if target_date_formatted != "-":
        target_date_formatted = f"{target_date_formatted[:4]}.{target_date_formatted[4:6]}.{target_date_formatted[6:]}"
    col1.metric(f"현재 환율 ({target_date_formatted})", current_exchange['rate'])

    if trade_data.get("status") == "success":
        target_month = trade_data.get("month")
        col2.metric(f"수출액 (단위: 백만$, {target_month})", f"$ {trade_data.get('exp')}")
        col3.metric(f"수입액 (단위: 백만$, {target_month})", f"$ {trade_data.get('imp')}")
        col4.metric(f"무역수지 (단위: 백만$, {target_month})", f"$ {trade_data.get('bal')}")
    else:
        col2.warning("통계 데이터를 불러오지 못했습니다.")   
    st.markdown("<hr>", unsafe_allow_html=True)

    # 중앙: 입력 필드
    with st.form("prediction_form"):
        st.markdown("#### 📝 분석 입력 필드")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**생산 및 납기 정보**")
            daily_out = st.number_input("일별출고량", min_value=0, value=100)
            capa = st.number_input("1일생산가능량(Capa)", min_value=0, value=150)
            delivery_date = st.date_input("납기일")  
        with c2:
            st.markdown("**현재 재고수량**")
            stock_finished = st.number_input("완제품", min_value=0, value=500)
            stock_wip = st.number_input("제공품", min_value=0, value=200)
            stock_part1 = st.number_input("부품1", min_value=0, value=1000)
        with c3:
            st.markdown("**주문 및 리드타임 정보**")
            order_vol = st.number_input("주문량 (고객/프로젝트별)", min_value=0, value=3000)
            lead_time_part1 = st.number_input("부품1 리드타임 (일)", min_value=0, value=14)
            
        st.markdown("<br>", unsafe_allow_html=True)
        method = st.selectbox("예측 방법 선택", ["ARIMA", "지수평활법", "이동평균법"])
        forecast_months = st.slider("예측 기간 선택 (개월)", 1, 12, 3)
        submitted = st.form_submit_button("📊 분석 시작", use_container_width=True)

    # 하단: 결과 필드
    if submitted:
        user_input_data = {
            "daily_out": daily_out,
            "capa": capa,
            "delivery_date": str(delivery_date),
            "stock_finished": stock_finished,
            "stock_wip": stock_wip,
            "stock_part1": stock_part1,
            "order_vol": order_vol,
            "lead_time_part1": lead_time_part1,
            "method": method,
            "forecast_months": forecast_months
        }
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 📈 수요예측 분석 결과")

        with st.spinner(f"AI 모델({method})을 활용하여 데이터를 분석하고 있습니다..."):
            try:
                response = requests.post(f"{API_URL}/predictions/mass_production", json=user_input_data)
                if response.status_code == 200:
                    result = response.json()
                    
                    tab1, tab2, tab3 = st.tabs(["주문량 예측", "리드타임 예측", "안전재고 예측"])
                    
                    with tab1:
                        df_order_hist = pd.DataFrame([result["order_volume"]["history"]])
                        df_order_pred = pd.DataFrame([result["order_volume"]["prediction"]])
                        fig1 = draw_prediction_chart(df_order_hist, df_order_pred, "주문량 추이 및 예측", "주문 수량(개)", '#007BFF', '#20B2AA')
                        st.plotly_chart(fig1, use_container_width=True)

                    with tab2:
                        df_lead_hist = pd.DataFrame([result["lead_time"]["history"]])
                        df_lead_pred = pd.DataFrame([result["lead_time"]["prediction"]])
                        fig2 = draw_prediction_chart(df_lead_hist, df_lead_pred, "리드타임 변동 및 예측", "리드타임(일)", '#FF8C00', '#FFD700')
                        st.plotly_chart(fig2, use_container_width=True)

                    with tab3:
                        df_safe_hist = pd.DataFrame([result["safety_stock"]["history"]])
                        df_safe_pred = pd.DataFrame([result["safety_stock"]["prediction"]])
                        fig3 = draw_prediction_chart(df_safe_hist, df_safe_pred, "안전재고 산출 및 예측", "안전재고 수량(개)", '#8A2BE2', '#FF69B4')
                        st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.error(f"분석 서버 오류 발생: HTTP {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("백엔드 서버와 연결할 수 없습니다. 서버가 켜져 있는지 확인해 주세요!")
            except Exception as e:
                st.error(f"예측 중 알 수 없는 오류가 발생했습니다: {e}")


def prediction_view():
    st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>단계 선택</div>", unsafe_allow_html=True)
    menu_selection = st.sidebar.radio(" ", ["양산 단계", "아이디어 단계", "시제품 단계"])
    
    if menu_selection == "양산 단계":
        mass_production_view()
    elif menu_selection == "아이디어 단계":
        st.info("🛠️ 아이디어 단계 화면은 준비 중입니다.")
    elif menu_selection == "시제품 단계":
        st.info("🛠️ 시제품 단계 화면은 준비 중입니다.")