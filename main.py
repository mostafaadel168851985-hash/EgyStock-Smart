import streamlit as st
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd

# 1. إعدادات الهوية البصرية (ستايل التليجرام الاحترافي)
st.set_page_config(page_title="Stock Expert", page_icon="📈")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .brand-title { 
        color: #FFFFFF !important; font-family: 'Arial Black', sans-serif; 
        font-size: 32px; text-align: center; margin: 20px 0;
    }
    .telegram-card {
        background: #ffffff; padding: 22px; border-radius: 12px;
        color: #000000 !important; max-width: 480px;
        direction: rtl; text-align: right; margin: auto;
        font-family: 'Segoe UI', Tahoma, sans-serif; border: 1px solid #ddd;
    }
    .price-val { 
        font-size: 45px; color: #d32f2f; font-weight: 900; 
        font-family: 'monospace'; display: block; margin: 2px 0;
    }
    .line { border-top: 1px solid #eee; margin: 12px 0; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_live_data(ticker):
    """محرك جلب البيانات اللحظية - خطة أ"""
    try:
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=7)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # سحب السعر الخام بدون تقريب
        p_text = soup.find('div', {'class': 'market-summary__last-price'}).text.strip().replace(',', '')
        price = float(p_text)
        change = soup.find('div', {'class': 'market-summary__change-percent'}).text.strip()
        turnover = soup.find('div', {'class': 'market-summary__value'}).text.strip()
        
        return price, change, turnover
    except:
        return None, None, None

def get_technical_analysis(ticker, current_price, turnover_text):
    """حساب الاتجاه والسيولة النسبية - خطة ب"""
    try:
        stock = yf.Ticker(f"{ticker}.CA")
        # سحب أقل داتا ممكنة عشان ميهنجش
        df = stock.history(period="30d")
        
        if df.empty: return "غير متوفر", "غير متوفر", "طبيعية ⚖️", "مراقبة"

        # 1. الاتجاهات
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        short_t = "صاعد 📈" if current_price > ma20 else "هابط 📉"
        mid_t = "صاعد 📈" if current_price > ma50 else "هابط 📉"

        # 2. حساب السيولة النسبية
        avg_val = (df['Close'] * df['Volume']).tail(10).mean()
        curr_val = 0
        t_txt = turnover_text.upper()
        if 'M' in t_txt: curr_val = float(t_txt.replace('M','')) * 1_000_000
        elif 'K' in t_txt: curr_val = float(t_txt.replace('K','')) * 1_000
        else: curr_val = float(t_txt.replace(',',''))
        
        ratio = curr_val / avg_val if avg_val > 0 else 1
        liq_label = "طبيعية ⚖️"
        if ratio > 1.7: liq_label = "انفجارية 🔥🚀"
        elif ratio > 1.2: liq_label = "عالية 🔥"

        # 3. التوصية
        rec = "شراء / احتفاظ ✅" if short_t == "صاعد 📈" and ratio > 1.1 else "مراقبة / حذر ⚠️"
        
        return short_t, mid_t, liq_label, rec
    except:
        return "جاري التحديث", "جاري التحديث", "طبيعية ⚖️", "مراقبة"

st.markdown('<div class="brand-title">📈 My Smart Stock Helper</div>', unsafe_allow_html=True)
ticker_input = st.text_input("🔍 ادخل رمز السهم (MOED, ATQA, CRST):", "").strip().upper()

if ticker_input:
    # محاولة جلب السعر أولاً (الأهم)
    with st.spinner('بنسحب البيانات اللحظية...'):
        p, c, t = get_live_data(ticker_input)
    
    if p:
        # محاولة التحليل (لو فشل ميبوظش الكارت)
        with st.spinner('بحلل السيولة والاتجاه...'):
            st_trend, mt_trend, liq, rec = get_technical_analysis(ticker_input, p, t)
        
        h1, h2 = p * 1.03, p * 1.05
        d1, stop = p * 0.97, p * 0.94

        st.markdown(f"""
        <div class="telegram-card">
            <b>💎 التقرير الشامل لـ {ticker_input}</b>
            <div class="line"></div>
            💰 <b>السعر اللحظي:</b>
            <span class="price-val">{p:.3f}</span>
            📈 <b>التغير:</b> <span style="color:{"green" if "+" in c else "red"}; font-weight:bold;">{c}</span>
            <div class="line"></div>
            🧭 <b>تحليل الاتجاه:</b><br>
            🔹 مدى قصير (20 يوم): <b>{st_trend}</b><br>
            🔹 مدى متوسط (50 يوم): <b>{mt_trend}</b>
            <div class="line"></div>
            💧 <b>نبض السيولة (نسبي):</b><br>
            قيمة تداول اليوم: {t}<br>
            حالة السيولة: <b>{liq}</b>
            <div class="line"></div>
            🚀 <b>الأهداف:</b> {h1:.3f} | {h2:.3f}<br>
            🛡️ <b>الدعم:</b> {d1:.3f} | 🛑 <b>الوقف: {stop:.3f}</b>
            <div class="line"></div>
            📢 <b>التوصية النهائية:</b> <span style="font-size: 18px; font-weight: bold; color: #d32f2f;">{rec}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ الرمز غير متاح حالياً على مباشر، تأكد من كتابته بشكل صحيح.")
