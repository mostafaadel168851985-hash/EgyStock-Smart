import streamlit as st
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات الهوية البصرية (أبيض فاقع ومنور)
st.set_page_config(page_title="My Smart Stock Helper", page_icon="🚀")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .brand-title { 
        color: #FFFFFF !important; 
        font-family: 'Arial Black', sans-serif; 
        font-size: 35px; text-align: center; margin: 20px 0;
        text-shadow: 0px 0px 15px rgba(255,255,255,0.7);
    }
    .telegram-card {
        background: #ffffff; padding: 25px; border-radius: 20px;
        color: #000000 !important; max-width: 500px;
        direction: rtl; text-align: right; margin: auto;
    }
    .price-val { 
        font-size: 45px; color: #d32f2f; font-weight: 900; 
        font-family: 'monospace'; line-height: 1;
    }
    .line { border-top: 2px solid #000; margin: 15px 0; opacity: 0.1; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# دالة ذكية لسحب السعر (مباشر) - لا تتوقف أبداً
def get_live_mubasher(ticker):
    try:
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        price_tag = soup.find('div', {'class': 'market-summary__last-price'})
        change_tag = soup.find('div', {'class': 'market-summary__change-percent'})
        turnover_tag = soup.find('div', {'class': 'market-summary__value'})
        
        if price_tag:
            p = float(price_tag.text.strip().replace(',', ''))
            c = change_tag.text.strip() if change_tag else "0.00%"
            t = turnover_tag.text.strip() if turnover_tag else "N/A"
            return p, c, t
    except: return None, None, None
    return None, None, None

# دالة تحليل الاتجاه (ياهو فاينانس) - معالجة أخطاء ذكية
def get_history_analysis(ticker, current_price):
    try:
        # بنحاول نجيب بيانات قصيرة عشان ميهنجش
        data = yf.download(f"{ticker}.CA", period="150d", progress=False)
        if not data.empty:
            ma20 = float(data['Close'].rolling(20).mean().iloc[-1])
            ma50 = float(data['Close'].rolling(50).mean().iloc[-1])
            
            short_t = "صاعد 📈" if current_price > ma20 else "هابط 📉"
            mid_t = "صاعد 📈" if current_price > ma50 else "هابط 📉"
            
            # حساب السيولة النسبية
            avg_vol = (data['Close'] * data['Volume']).tail(10).mean()
            return short_t, mid_t, avg_vol
    except: pass
    return "غير متوفر ⚠️", "غير متوفر ⚠️", 0

st.markdown('<div class="brand-title">🚀 My Smart Stock Helper</div>', unsafe_allow_html=True)
ticker = st.text_input("🔍 ادخل رمز السهم (TMGH, MOED, ATQA):", "").strip().upper()

if ticker:
    # 1. نجيب السعر اللحظي أولاً (ده أهم حاجة)
    with st.spinner('بنسحب السعر اللحظي...'):
        p_live, c_live, t_live = get_live_mubasher(ticker)
    
    if p_live:
        # 2. نحاول نجيب التحليل الفني (لو فشل مش هيوقف البرنامج)
        with st.spinner('بحلل الاتجاهات...'):
            short_term, mid_term, avg_v = get_history_analysis(ticker, p_live)
        
        # حساب السيولة
        liq_status = "عادية ⚖️"
        if "M" in t_live:
            curr_v = float(t_live.replace('M','').replace(',','')) * 1_000_000
            if avg_v > 0 and curr_v > (avg_v * 1.5): liq_status = "انفجارية 🔥🚀"
            elif avg_v > 0 and curr_v > avg_v: liq_status = "عالية 🔥"

        # حساب الأهداف
        h1, h2 = p_live * 1.03, p_live * 1.05
        d1, stop = p_live * 0.97, p_live * 0.94

        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 22px; font-weight: bold;">💎 التقرير الشامل لـ {ticker}</div>
            <div class="line"></div>
            💰 <b>السعر اللحظي بدقة:</b> <br>
            <span class="price-val">{p_live:.3f}</span> <small>{c_live}</small>
            <div class="line"></div>
            🧭 <b>اتجاه السهم:</b><br>
            🔹 مدى قصير (20 يوم): <b>{short_term}</b><br>
            🔹 مدى متوسط (50 يوم): <b>{mid_term}</b>
            <div class="line"></div>
            💧 <b>تحليل السيولة:</b><br>
            قيمة تداول اليوم: {t_live}<br>
            الحالة: <b>{liq_status}</b>
            <div class="line"></div>
            🚀 <b>الأهداف:</b> {h1:.3f} - {h2:.3f}<br>
            🛡️ <b>الدعم:</b> {d1:.3f} | 🛑 <b>الوقف: {stop:.3f}</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("الرمز غير صحيح أو هناك ضغط على السيرفر، جرب مرة أخرى.")
