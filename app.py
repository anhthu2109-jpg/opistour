import streamlit as st
import pandas as pd
from datetime import datetime, date
import math
import pymysql
from google import genai  # Chỉ dùng SDK chính thức mới

# Dán API Key của bạn vào đây
GEMINI_API_KEY = "AQ.Ab8RN6Im4364rpP31Dyfxf1h6utzE7Yrouc2hIDpr3GySRYFjg" 

# Khởi tạo client chính xác
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Lỗi khởi tạo Gemini Client: {e}")
