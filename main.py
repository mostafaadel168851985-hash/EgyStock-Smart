import streamlit as st
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd

# 1. تصميم الواجهة (نفس شكل كروت التليجرام الاحترافية)
st.set_page_config(page_title="EGX Live Analyst", page_icon="💹")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .brand-title { color: #FFFFFF !important; font-family: 'Arial'; font-size: 30px; text-align: center; margin: 15px 0; }
    .telegram-card {
        background: #ffffff; padding: 20px; border-radius: 15px;
        color: #000000 !important; max-width: 450px;
        direction: rtl; text-align: right; margin: auto;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    .price-val { font-size: 48px; color: #d32f2f; font-weight: 900; font-family: 'monospace'; }
    .line { border-top: 1px solid #eee; margin: 10px 0; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_live_mubasher(ticker):
    """سحب السعر اللحظي والسيولة من مباشر مع حماية من الحظر"""
    try:
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        response = session.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # البحث عن السعر بدقة (الكسر العشري)
        price_tag = soup.find('div', {'class': 'market-summary__last-price'})
        change_tag = soup.find('div', {'class': 'market-summary__change-percent'})
        turnover_tag = soup.find('div', {'class': 'market-summary__value'})
        
        if price_tag:
            p = float(price_tag.text.strip().replace(',', ''))
            c = change_tag.text.strip()
            t = turnover_tag.text.strip()
            return p, c, t
    except:
        return None, None, None

def get_technical_vibes(ticker, current_price, turnover_text):
    """تحليل الاتجاه والسيولة النسبية"""
    try:
        stock = yf.Ticker(f"{ticker}.CA")
        df = stock.history(period="30d")
        if df.empty: return "غير محدد", "طبيعية ⚖️", "مراقبة"

        # 1. الاتجاه (باستخدام المتوسط المتحرك 20)
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        trend = "صاعد 📈" if current_price > ma20 else "هابط 📉"

        # 2. تحليل السيولة (تحويل نص مباشر لرقم للمقارنة)
        curr_val = 0
        t_txt = turnover_text.upper()
        if 'M' in t_txt: curr_val = float(t_txt.replace('M','')) * 1_000_000
        elif 'K' in t_txt: curr_val = float(t_txt.replace('K','')) * 1_000
        else: curr_val = float(t_txt.replace(',',''))
        
        avg_val = (df['Close'] * df['Volume']).tail(10).mean()
        ratio = curr_val / avg_val if avg_val > 0 else 1
        
        liq_status = "طبيعية ⚖️"
        if ratio > 1.8: liq_status = "انفجارية 🔥🚀"
        elif ratio > 1.3: liq_status = "عالية 🔥"
        
        # 3. التوصية بناءً على (السعر + الاتجاه + السيولة)
        rec = "مراقبة 🛡️"
        if trend == "صاعد 📈" and ratio > 1.2: rec = "شراء / احتفاظ ✅"
        elif trend == "هابط 📉" and ratio > 1.5: rec = "تسييل / حذر ⚠️"

        return trend, liq_status, rec
    except:
        return "جاري التحليل", "طبيعية ⚖️", "مراقبة"

st.markdown('<div class="brand-title">🚀 EGX Smart Live Analyst</div>', unsafe_allow_html=True)
ticker = st.text_input("🔍 ادخل الرمز (مثلاً: MOED, ATQA, TMGH):", "").strip().upper()

if ticker:
    with st.spinner('بنجيب السعر اللحظي من شاشة التداول...'):
        p_live, c_live, t_live = get_live_mubasher(ticker)
        
    if p_live:
        trend, liq, recommendation = get_technical_vibes(ticker, p_live, t_live)
        
        # حساب الأهداف (3% و 5%)
        h1, h2 = p_live * 1.03, p_live * 1.05
        d1, stop = p_live * 0.97, p_live * 0.94

        st.markdown(f"""
        <div class="telegram-card">
            <b>💎 تقرير {ticker} اللحظي</b>
            <div class="line"></div>
            💰 <b>السعر اللحظي (مباشر):</b>
            <span class="price-val">{p_live:.3f}</span>
            📈 <b>التغير:</b> <span style="color:{"green" if "+" in c_live else "red"}; font-weight:bold;">{c_live}</span>
            <div class="line"></div>
            🧭 <b>الاتجاه الحالي:</b> <b>{trend}</b><br>
            💧 <b>قوة السيولة:</b> <b>{liq}</b><br>
            📊 <b>تداولات اليوم:</b> {t_live} ج.م
            <div class="line"></div>
            🚀 <b>المستهدفات:</b> {h1:.3f} | {h2:.3f}<br>
            🛑 <b>وقف الخسارة: {stop:.3f}</b>
            <div class="line"></div>
            📢 <b>التوصية:</b> <span style="font-size: 20px; color: #d32f2f; font-weight: bold;">{recommendation}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ الموقع لا يستجيب حالياً، جرب كتابة الرمز مرة أخرى (MOED).")
