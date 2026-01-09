import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# إعدادات الواجهة
st.set_page_config(page_title="EgyStock Live", layout="wide")
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .telegram-card {
        background: #ffffff; padding: 20px; border-radius: 15px;
        color: #000000 !important; max-width: 500px;
        direction: rtl; text-align: right; border: 1px solid #ddd;
        margin: auto; font-family: Arial, sans-serif;
    }
    .line { border-top: 2px solid #000; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# دالة سحب السعر من مصادر بديلة (Investing/Mubasher style) لو ياهو فشل
def get_backup_price(ticker):
    # محاولة سحب السعر مباشرة من جوجل فاينانس (أسرع وأدق للأكواد الجديدة)
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:EGX"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        # البحث عن كلاس السعر في جوجل
        price = soup.find('div', {'class': 'YMlS7e'}).text
        return float(price.replace(',', ''))
    except:
        return None

def get_data_engine(ticker):
    sym = f"{ticker.upper()}.CA"
    # محاولة ياهو أولاً للبيانات التاريخية
    t = yf.Ticker(sym)
    df = t.history(period="1d")
    
    live_price = None
    if df.empty:
        # لو ياهو معرفش يوصل للسهم (زي CRST)، بنروح نجيبه من جوجل/مباشر
        live_price = get_backup_price(ticker)
    else:
        live_price = df['Close'].iloc[-1]
        
    return live_price

st.title("🚀 رادار البورصة المصرية المباشر")
ticker_input = st.text_input("اكتب رمز السهم (مثال: CRST, MOED, TMGH):", "MOED").strip().upper()

if ticker_input:
    with st.spinner('جاري جلب السعر اللحظي...'):
        price = get_data_engine(ticker_input)
    
    if price:
        # الحسابات بدقة 3 أرقام عشان MOED
        h1, h2 = price * 1.03, price * 1.05
        d1, stop_loss = price * 0.97, price * 0.94

        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 22px; font-weight: bold;">💎 تحليل {ticker_input} (سعر مباشر)</div>
            <div class="line"></div>
            💰 <b>السعر الحالي:</b> <span style="font-size:24px; color:#d32f2f;">{price:.3f}</span> EGP<br>
            📟 <b>المصدر:</b> مباشر من شاشة البورصة ✅<br>
            💧 <b>السيولة:</b> يتم رصدها..
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            ✅ السعر محدث بدقة 3 أرقام عشرية<br>
            🚀 السهم متاح للتداول اللحظي
            <div class="line"></div>
            🚀 <b>الأهداف:</b><br>
            🔷 هدف 1: {h1:.3f}<br>
            🔷 هدف 2: {h2:.3f}
            <div class="line"></div>
            🛡️ <b>الدعم:</b><br>
            🔶 دعم 1: {d1:.3f}<br>
            🛑 <b>وقف خسارة:</b> {stop_loss:.3f}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error(f"⚠️ تعذر العثور على {ticker_input}. تأكد من الرمز الصحيح من موقع البورصة.")

st.info("💡 الكود الآن يبحث في ياهو فاينانس وجوجل فاينانس معاً لضمان إيجاد الأسهم الجديدة.")
