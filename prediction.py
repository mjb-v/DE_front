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

def get_prod_predictions(forecast_months: int):
    params = {'forecast_months': forecast_months}
    response = requests.get(f"{API_URL}/productions/predict/", params=params)
    if response.status_code == 200:
        data = response.json()
        pred_df = pd.DataFrame(data['predicted_productions']).rename(columns={"date": "날짜", "month_quantity": "생산 실적"})

        # 반올림, 쉼표 추가
        pred_df["생산 실적"] = pred_df["생산 실적"].round().astype(int).apply(lambda x: f"{x:,}")
        pred_df = pred_df[["날짜", "생산 실적"]].set_index("날짜").transpose()  
        return pred_df
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

def get_inven_predictions(forecast_months: int):
    params = {'forecast_months': forecast_months}
    response = requests.get(f"{API_URL}/material_invens/predict/", params=params)
    if response.status_code == 200:
        data = response.json()
        pred_df = pd.DataFrame(data['predicted_material_invens']).rename(columns={"date": "날짜", "month_amount": "매입 실적"})

        # 반올림, 쉼표 추가
        pred_df["매입 실적"] = pred_df["매입 실적"].round().astype(int).apply(lambda x: f"{x:,}")
        pred_df = pred_df[["날짜", "매입 실적"]].set_index("날짜").transpose()  
        return pred_df
    else:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return None

def highlight_prod(row):
    return ['background-color: #E3F2FD']*len(row)
def highlight_inven(row):
    return ['background-color: #FFF8E1']*len(row)

# ------------------------------------------------------------------------------------------------
def prediction_view():
    tab = st.sidebar.radio(" ", ["생산 수요 예측", "자재 수요 예측"])

    if tab == "생산 수요 예측":
        st.markdown("<h2 style='text-align: left; color: #007BFF;'>🔮 생산 수요 예측</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)

        st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>필터 설정</div>", unsafe_allow_html=True)
        current_year = datetime.today().year
        selected_year = st.sidebar.selectbox("년도 선택", list(range(2014, 2025)), index=list(range(2014, 2025)).index(current_year))

        df = get_prod_plan(selected_year)
        if df is not None:
            st.subheader(f"{selected_year}년도 생산 실적")
            st.markdown("""
                <style>
                .dataframe {
                    width: 80% !important;
                }
                </style>
                """, unsafe_allow_html=True)
            st.dataframe(df)

        # 예측 데이터
        forecast_months = st.slider("예측 기간 선택", min_value=1, max_value=12, value=3)
        pred_df = get_prod_predictions(forecast_months)
        if pred_df is not None:
            st.subheader(f"{forecast_months}개월 예측 데이터")
            st.dataframe(pred_df.style.apply(highlight_prod, axis=1).set_properties(**{'text-align': 'center'}))
            st.download_button(label="CSV로 다운로드", data=pred_df.to_csv(), file_name="예측보고서.csv", mime="text/csv")
        st.markdown("<hr style='border:1px solid #E0E0E0;'>", unsafe_allow_html=True)

        # 그래프: 현재 날짜 기준으로 지난 12개월 데이터만 추출
        current_year_data = get_prod_plan(current_year)
        last_year_data = get_prod_plan(current_year - 1)

        if current_year_data is not None and last_year_data is not None and pred_df is not None:
            all_data_df = pd.concat([last_year_data, current_year_data], axis=1)
            current_date = datetime.today()
            last_12_months = [(current_date.replace(day=1) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(12)]
            df_existing = all_data_df.loc[:, all_data_df.columns.isin(last_12_months)]

            fig = go.Figure()
            # 현재 데이터 그래프
            fig.add_trace(go.Scatter(x=df_existing.columns, y=df_existing.iloc[0],
                                    mode='lines+markers', name='현재 데이터',
                                    line=dict(color='#007BFF', width=3),
                                    marker=dict(color='#007BFF', size=8)))

            # 예측 데이터 그래프
            pred_df_with_last_value = pred_df.copy()
            last_value = df_existing.iloc[0, -1]
            pred_df_with_last_value.insert(0, df_existing.columns[-1], last_value)

            fig.add_trace(go.Scatter(
                x=pred_df_with_last_value.columns, 
                y=pred_df_with_last_value.iloc[0], 
                mode='lines+markers', 
                name='예측 데이터',
                line=dict(color='#20B2AA', dash='dash', width=3),
                marker=dict(color='#20B2AA', size=8)
            ))

            fig.update_layout(
                title="📈 생산 실적 및 수요 예측 그래프",
                xaxis_title="월",
                yaxis_title="생산 실적",
                plot_bgcolor='rgba(0, 0, 0, 0)',
                hovermode="x",
                font=dict(family="NanumGothic, sans-serif", size=14),
                title_font=dict(size=20, color="black"),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig)

    elif tab == "자재 수요 예측":
        st.markdown("<h2 style='text-align: left; color: #FF8C00;'>🔮 자재 수요 예측</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid #E0E0E0; margin: 2px 0 25px 0;'>", unsafe_allow_html=True)

        st.sidebar.markdown("<div class='sidebar-section sidebar-subtitle'>필터 설정</div>", unsafe_allow_html=True)
        current_year = datetime.today().year
        selected_year = st.sidebar.selectbox("년도 선택", list(range(2014, 2025)), index=list(range(2014, 2025)).index(current_year))

        df = get_inven_plan(selected_year)
        if df is not None:
            st.subheader(f"{selected_year}년도 매입 실적")
            st.markdown("""
                <style>
                .dataframe {
                    width: 80% !important;
                }
                </style>
                """, unsafe_allow_html=True)
            st.dataframe(df)

        # 예측 데이터
        forecast_months = st.slider("예측 기간 선택", min_value=1, max_value=12, value=3)
        pred_df = get_inven_predictions(forecast_months)
        if pred_df is not None:
            st.subheader(f"{forecast_months}개월 예측 데이터")
            st.dataframe(pred_df.style.apply(highlight_inven, axis=1).set_properties(**{'text-align': 'center'}))
            st.download_button(label="CSV로 다운로드", data=pred_df.to_csv(), file_name="예측보고서.csv", mime="text/csv")
        st.markdown("<hr style='border:1px solid #E0E0E0;'>", unsafe_allow_html=True)

        # 그래프: 현재 날짜 기준으로 지난 12개월 데이터만 추출
        current_year_data = get_inven_plan(current_year)
        last_year_data = get_inven_plan(current_year - 1)

        if current_year_data is not None and last_year_data is not None and pred_df is not None:
            all_data_df = pd.concat([last_year_data, current_year_data], axis=1)
            current_date = datetime.today()
            last_12_months = [(current_date.replace(day=1) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(12)]
            df_existing = all_data_df.loc[:, all_data_df.columns.isin(last_12_months)]

            fig = go.Figure()
            # 현재 데이터 그래프
            fig.add_trace(go.Scatter(x=df_existing.columns, y=df_existing.iloc[0],
                                    mode='lines+markers', name='현재 데이터',
                                    line=dict(color='#FF8C00', width=3),
                                    marker=dict(color='#FF8C00', size=8)))

            # 예측 데이터 그래프
            pred_df_with_last_value = pred_df.copy()
            last_value = df_existing.iloc[0, -1]
            pred_df_with_last_value.insert(0, df_existing.columns[-1], last_value)

            fig.add_trace(go.Scatter(
                x=pred_df_with_last_value.columns, 
                y=pred_df_with_last_value.iloc[0], 
                mode='lines+markers', 
                name='예측 데이터',
                line=dict(color='#FFD700', dash='dash', width=3),
                marker=dict(color='#FFD700', size=8)
            ))

            fig.update_layout(
                title="📈 매입 실적 및 수요 예측 그래프",
                xaxis_title="월",
                yaxis_title="매입 실적",
                plot_bgcolor='rgba(0, 0, 0, 0)',
                hovermode="x",
                font=dict(family="NanumGothic, sans-serif", size=14),
                title_font=dict(size=20, color="black"),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig)
