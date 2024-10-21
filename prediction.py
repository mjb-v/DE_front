import pandas as pd
import streamlit as st
import requests
from datetime import datetime
from matplotlib import font_manager, rc
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

# FastAPI URL
load_dotenv()
API_URL = os.getenv("API_URL")

def get_all_plan(year: int):
    response = requests.get(f"{API_URL}/plans/rate/{year}")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data).rename(columns={"year":"년도", "month":"월", "business_amount":"생산 실적"})
        df["년도"] = df["년도"].astype(str)
        df["날짜"] = df.apply(lambda x: f"{x['년도']}-{int(x['월']):02d}", axis=1)
        df = df[["날짜", "생산 실적"]].set_index("날짜").transpose()
        return df
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

def get_predictions(forecast_months: int):
    params = {'forecast_months': forecast_months}
    response = requests.get(f"{API_URL}/productions/predict/", params=params)
    if response.status_code == 200:
        data = response.json()
        pred_df = pd.DataFrame(data['predicted_productions']).rename(columns={"date": "날짜", "month_quantity": "생산 실적"})

        # 반올림, 쉼표 추가
        pred_df["생산 실적"] = pred_df["생산 실적"].round().astype(int)
        pred_df["생산 실적"] = pred_df["생산 실적"].apply(lambda x: f"{x:,}")
        pred_df = pred_df[["날짜", "생산 실적"]].set_index("날짜").transpose()  
        return pred_df
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

def highlight_prediction(row):
    return ['background-color: rgba(255, 99, 71, 0.5)']*len(row)

# ------------------------------------------------------------------------------------------------
def prediction_view():
    st.markdown("<h2 style='text-align: left; color: #ff4747;'>생산 수요 예측</h2>", unsafe_allow_html=True)
    st.markdown("""<div class="custom-line"></div>""", unsafe_allow_html=True)
    current_year = datetime.today().year
    selected_year = st.sidebar.selectbox("년도 선택", list(range(2014, 2025)), index=list(range(2014, 2025)).index(current_year))

    df = get_all_plan(selected_year)
    if df is not None:
        st.subheader(f"{selected_year}년도 생산 실적")
        st.dataframe(df)

    # 예측 기간 선택 슬라이더
    st.markdown("<h3 style='text-align: left;'>몇 달치 예측을 볼까요?</h3>", unsafe_allow_html=True)
    forecast_months = st.slider(" ", min_value=1, max_value=12, value=3)

    # 예측 데이터
    pred_df = get_predictions(forecast_months)
    if pred_df is not None:
        st.subheader(f"{forecast_months}개월 예측 데이터")
        st.dataframe(pred_df.style.apply(highlight_prediction, axis=1))
        st.download_button(label="CSV로 다운로드", data=pred_df.to_csv(), file_name="예측보고서.csv", mime="text/csv")

    st.markdown("""<div class="custom-line"></div>""", unsafe_allow_html=True)
    # 그래프
    if df is not None and pred_df is not None:
        fig = go.Figure()

        # 현재 날짜 기준으로 지난 12개월 데이터만 추출
        current_date = datetime.today()
        last_12_months = [(current_date.replace(day=1) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(12)]
        df_existing = df.loc[:, df.columns.isin(last_12_months)]

        # 현재 데이터 그래프
        fig.add_trace(go.Scatter(x=df_existing.columns, y=df_existing.iloc[0],
                                 mode='lines+markers', name='현재 데이터'))

        # 예측 데이터 그래프
        pred_df_with_last_value = pred_df.copy()
        last_value = df_existing.iloc[0, -1]
        pred_df_with_last_value.insert(0, df_existing.columns[-1], last_value)

        fig.add_trace(go.Scatter(x=pred_df_with_last_value.columns, y=pred_df_with_last_value.iloc[0],
                                 mode='lines+markers', name='예측 데이터',
                                 line=dict(color='rgba(255, 99, 71, 0.8)', dash='dash'),
                                 marker=dict(color='rgba(255, 99, 71, 0.8)', size=8)))

        fig.update_layout(
            title="생산 실적 및 수요 예측 그래프",
            xaxis_title="월",
            yaxis_title="생산 실적",
            plot_bgcolor='rgba(0, 0, 0, 0)',
            hovermode="x"
        )
        st.plotly_chart(fig)