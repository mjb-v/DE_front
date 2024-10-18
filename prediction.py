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
        df = df[["년도", "월", "생산 실적"]]
        return df
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

def get_predictions(forecast_months: int):
    params = {'forecast_months': forecast_months}
    response = requests.get(f"{API_URL}/productions/predict/", params=params)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data['predicted_productions']).rename(columns={"date": "날짜", "month_quantity": "생산 실적"})
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

def highlight_prediction(row):
    return ['background-color: lightgreen']*len(row)

# ------------------------------------------------------------------------------------------------
def prediction_view():
    st.markdown("<h2 style='text-align: left; color: #008080;'>수요 예측</h2>", unsafe_allow_html=True)
    current_year = datetime.today().year
    selected_year = st.sidebar.selectbox("년도 선택", list(range(2014, 2025)), index=list(range(2014, 2025)).index(current_year))
    df = get_all_plan(selected_year)
    pred_df = get_predictions(3)

    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(df)

    with col2:
        st.dataframe(pred_df.style.apply(highlight_prediction, axis=1))
        st.download_button(label="CSV로 다운로드", data=pred_df.to_csv(), file_name="예측보고서.csv", mime="text/csv")

    # 기존 데이터 그래프
    fig = px.line(df, x='월', y='생산 실적', title='수요 예측 그래프', labels={'날짜': '날짜', '생산 실적': '생산 실적'})

    # 예측 데이터 추가 (점선, 부드러운 색상)
    fig.add_trace(go.Scatter(x=pred_df['날짜'], y=pred_df['생산 실적'],
                            mode='lines+markers',  # 선 + 마커
                            name='예측 데이터',
                            line=dict(color='rgba(255, 99, 71, 0.8)', dash='dash'),  # 선 색과 점선 스타일
                            marker=dict(color='rgba(255, 99, 71, 0.8)', size=8)))  # 마커 스타일
    fig.update_layout(
        title="생산 실적 및 수요 예측 그래프",
        xaxis_title="날짜",
        yaxis_title="생산 실적",
        plot_bgcolor='rgba(0, 0, 0, 0)',
        hovermode="x"
    )
    st.plotly_chart(fig)