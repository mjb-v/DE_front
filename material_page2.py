from matplotlib import font_manager, rc
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime

font_path = 'NanumGothic-Regular.ttf'
font_manager.fontManager.addfont(font_path)
rc('font', family='NanumGothic')

# FastAPI URL
API_URL = "http://127.0.0.1:8000"

# 한글 컬럼명으로 변환
def translate_data(data):
    translation_dict = {
        "year": "년도",
        "month": "월",
        "business_plan": "사업계획",
        "business_amount": "실적",
        "business_achievement_rate": "사업달성율",
        "item_number": "품번",
        "item_name": "품명",
        "client_code": "거래처코드",
        "previous_amount": "전월실적",
        "current_amount": "당월실적",
        "growth_rate": "증감율",
        "client": "거래처명", # (dropdown: (주)금성오토텍, 
        "model": "모델구분", # (dropdown: 가정, 건조기, 세탁기, 식기세척기, 에어컨, 중장비)
        "item_category": "품목구분", # (dropdown: 원재료, 부재료, 재공품, 제품, 반제품)
        "process": "공정구분", # (drodown: 검사/조립, 사출)
        "quantity": "계획수량"
    }
    return pd.DataFrame(data).rename(columns=translation_dict)

# ----------------------------------------------------------------
def material_page2_view():
    pass
