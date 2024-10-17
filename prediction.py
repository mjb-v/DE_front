import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# 2023, 2024년 데이터
data_2024 = {'연도': [2024]*9,
             '월': ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월'],
             '생산 실적': [617476580, 607604059, 736014563, 1052532333, 984630468, 816179673, 690925169, 608094550, 636730271]}

df_2024 = pd.DataFrame(data_2024)
data_2023 = {'연도': [2023]*12,
             '월': ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
             '생산 실적': [501219048, 837546776, 810525904, 670187228, 992666152, 742121013, 659425878, 530697949, 486715432, 742281109, 775249190, 585328265]}

df_2023 = pd.DataFrame(data_2023)
df_2024['날짜'] = pd.to_datetime(df_2024['연도'].astype(str) + '-' + df_2024['월'], format='%Y-%m월').dt.strftime('%Y-%m')
df_2023['날짜'] = pd.to_datetime(df_2023['연도'].astype(str) + '-' + df_2023['월'], format='%Y-%m월').dt.strftime('%Y-%m')

df = pd.concat([df_2023, df_2024], ignore_index=True)
df = df[['날짜', '생산 실적']]

'''
# 분석기법
# 1. SMA - 단순하게 이전 데이터에서 계산
df['이동 평균'] = df['생산 실적'].rolling(window=3).mean()

# 2. 지수평활법 - 최근 데이터에 가중치를 더 줘서 계산
from statsmodels.tsa.holtwinters import ExponentialSmoothing

model = ExponentialSmoothing(df['생산 실적'], trend='add', seasonal='add', seasonal_periods=12)
model_fit = model.fit()
pred = model_fit.forecast(steps=3)
round(pred)
'''

def highlight_prediction(row):
    return ['background-color: yellow']*len(row)

# ------------------------------------------------------------------------------------------------
def prediction_view():
    current_year = datetime.today().year
    selected_year = st.sidebar.selectbox("년도 선택", list(range(2014, 2025)), index=list(range(2014, 2025)).index(current_year))

    # ARIMA 모델
    model = ARIMA(df['생산 실적'], order=(5,1,0))
    model_fit = model.fit()
    pred = model_fit.forecast(steps=3)
    future_dates = pd.date_range(df['날짜'].max(), periods=4, freq='ME')[1:]
    pred_df = pd.DataFrame({'날짜': future_dates.strftime('%Y-%m'), '생산 실적': round(pred, 0)})

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"### {selected_year}년 데이터")
        st.dataframe(df[df['날짜'].str.startswith(str(selected_year))])
    with col2:
        st.write("### 3개월 예측 데이터")
        st.dataframe(pred_df.style.apply(highlight_prediction, axis=1))

    # 그래프
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['날짜'], df['생산 실적'], color='blue', marker='o')
    ax.plot(pred_df['날짜'], pred_df['생산 실적'], label='예측', color='red', linestyle='--', marker='x')
    ax.set_title('수요 예측 그래프')
    ax.set_xlabel('날짜')
    ax.set_ylabel('생산 실적')

    plt.xticks(rotation=45)
    plt.legend()

    st.pyplot(fig)