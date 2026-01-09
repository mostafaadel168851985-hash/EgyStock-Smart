import streamlit as st
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd

# 1. تنسيق الواجهة (White & Black Pro)
st.set_page_config(page_title="My Smart Stock Helper", page_icon="🚀")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .brand-title { 
        color: #FFFFFF !important; font-family: 'Arial Black', sans-serif; 
        font-size: 32px; text-align: center; margin: 20px 0;
        text-shadow: 0px 0px 10px rgba(255,255,255,0.3);
    }
    .telegram-card {
        background: #ffffff; padding: 22px; border-radius: 12px;
        color: #000000 !important; max-width: 460px;
        direction: rtl; text-align: right; margin: auto;
        font-family: 'Segoe UI', Tahoma, sans-serif; border: 1px solid #ddd;
    }
    .price-val { 
        font-size: 42px; color: #d32f2f; font-weight: 800; 
        font-family: 'monospace'; display: block; margin: 2px 0;
    }
    .line { border-top: 1px solid #eee; margin: 12px 0; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_comprehensive_analysis(ticker):
    try:
        # أ- جلب السعر والسيولة اللحظية من مباشر
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        price = float(soup.find('div', {'class': 'market-summary__last-price'}).text.strip().replace(',', ''))
        change = soup.find('div', {'class': 'market-summary__change-percent'}).text.strip()
        turnover_text = soup.find('div', {'class': 'market-summary__value'}).text.strip()
        
        # ب- التحليل التاريخي من ياهو (متوسط 20 يوم والسيولة)
        stock = yf.Ticker(f"{ticker}.CA")
        hist = stock.history(period="30d")
        
        analysis = {'short_trend': "هابط 📉", 'liq_label': "طبيعية ⚖️", 'rec': "مراقبة 🛡️"}
        
        if not hist.empty:
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            avg_vol = (hist['Close'] * hist['Volume']).tail(15).mean()
            
            # حساب القيمة الرقمية للسيولة اللحظية
            curr_val = 0
            t_txt = turnover_text.upper()
            if 'M' in t_txt: curr_val = float(t_txt.replace('M','')) * 1_000_000
            elif 'K' in t_txt: curr_val = float(t_txt.replace('K','')) * 1_000
            else: curr_val = float(t_txt.replace(',',''))
            
            # 1. تحديد الاتجاه
            is_up = price > ma20
            analysis['short_trend'] = "صاعد 📈" if is_up else "هابط 📉"
            
            # 2. تحديد السيولة النسبية
            ratio = curr_val / avg_vol if avg_vol > 0 else 1
            if ratio > 1.6: analysis['liq_label'] = "انفجارية 🔥🚀"
            elif ratio > 1.2: analysis['liq_label'] = "عالية 🔥"
            else: analysis['liq_label'] = "طبيعية ⚖️"
            
            # 3. محرك التوصية الذكي
            if is_up and ratio > 1.2 and "+" in change:
                analysis['rec'] = "شراء قوي 🚀"
            elif is_up or ratio > 1.5:
                analysis['rec'] = "احتفاظ / إيجابي ✅"
            elif not is_up and "-" in change:
                analysis['rec'] = "جني أرباح / خروج 🛑"
            else:
                analysis['rec'] = "مراقبة / حياد ⚖️"

        return price, change, turnover_text, analysis
    except: return None, None, None, None

st.markdown('<div class="brand-title">📈 My Smart Stock Helper</div>', unsafe_allow_html=True)
ticker_input = st.text_input("🔍 ادخل رمز السهم (مثلاً MOED, ATQA, CRST):", "").strip().upper()

if ticker_input:
    with st.spinner('جاري المسح الفني واللحظي...'):
        price, change, turnover, result = get_comprehensive_analysis(ticker_input)
    
    if price:
        h1, h2 = price * 1.03, price * 1.05
        d1, stop = price * 0.97, price * 0.94
        
        st.markdown(f"""
        <div class="telegram-card">
            <b>💎 التحليل الشامل لـ {ticker_input}</b>
            <div class="line"></div>
            💰 <b>السعر اللحظي (دقة 100%):</b>
            <span class="price-val">{price:.3f}</span>
            📈 <b>التغير:</b> <span style="color:{"green" if "+" in change else "red"}; font-weight:bold;">{change}</span>
            <div class="line"></div>
            🧭 <b>الاتجاه القصير (20 يوم):</b> <b>{result['short_trend']}</b><br>
            💧 <b>نبض السيولة (نسبة للمتوسط):</b> <b>{result['liq_label']}</b>
            <div class="line"></div>
            🚀 <b>الأهداف:</b> {h1:.3f} | {h2:.3f}<br>
            🛡️ <b>الدعم:</b> {d1:.3f} | 🛑 <b>الوقف: {stop:.3f}</b>
            <div class="line"></div>
            📢 <b>التوصية النهائية:</b> <span style="font-size: 18px; font-weight: bold; color: #d32f2f;">{result['rec']}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ تأكد من الرمز (مثال: CRST وليس CRST.CA)")
