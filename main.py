import streamlit as st
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd

# 1. إعدادات الهوية البصرية (الاسم الأبيض المنور)
st.set_page_config(page_title="My Smart Stock Helper", page_icon="📈")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .brand-title { 
        color: #FFFFFF !important; 
        font-family: 'Arial Black', sans-serif; 
        font-size: 35px; text-align: center; margin: 20px 0;
        text-shadow: 0px 0px 15px rgba(255,255,255,0.5);
    }
    .telegram-card {
        background: #ffffff; padding: 25px; border-radius: 20px;
        color: #000000 !important; max-width: 500px;
        direction: rtl; text-align: right; margin: auto;
    }
    .price-val { 
        font-size: 42px; color: #d32f2f; font-weight: 900; 
        font-family: 'monospace'; line-height: 1;
    }
    .trend-box { padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 14px; }
    .trend-up { background-color: #e8f5e9; color: #2e7d32; }
    .trend-down { background-color: #ffebee; color: #c62828; }
    .line { border-top: 2px solid #000; margin: 15px 0; opacity: 0.1; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def analyze_stock(ticker, current_price):
    try:
        stock = yf.Ticker(f"{ticker}.CA")
        hist = stock.history(period="1y") # سحب بيانات سنة للتحليل الطويل
        if hist.empty: return None
        
        # حساب المتوسطات
        ma20 = hist['Close'].rolling(20).mean().iloc[-1]
        ma50 = hist['Close'].rolling(50).mean().iloc[-1]
        ma200 = hist['Close'].rolling(200).mean().iloc[-1]
        
        # تحديد الاتجاهات
        short_term = "صاعد 📈" if current_price > ma20 else "هابط 📉"
        mid_term = "صاعد 📈" if current_price > ma50 else "هابط 📉"
        long_term = "صاعد 📈" if current_price > ma200 else "هابط 📉"
        
        # قوة الاتجاه (RSI)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        return {
            "short": short_term, "mid": mid_term, "long": long_term,
            "rsi": rsi, "ma50": ma50
        }
    except: return None

def get_mubasher_live(ticker):
    try:
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        price = float(soup.find('div', {'class': 'market-summary__last-price'}).text.strip().replace(',', ''))
        change = soup.find('div', {'class': 'market-summary__change-percent'}).text.strip()
        turnover = soup.find('div', {'class': 'market-summary__value'}).text.strip()
        return price, change, turnover
    except: return None, None, None

st.markdown('<div class="brand-title">🚀 My Smart Stock Helper</div>', unsafe_allow_html=True)
ticker = st.text_input("🔍 ادخل رمز السهم (مثلاً TMGH, MOED, ATQA):", "").strip().upper()

if ticker:
    with st.spinner('جاري المسح الشامل للاتجاهات والسيولة...'):
        price, change, turnover = get_mubasher_live(ticker)
        analysis = analyze_stock(ticker, price)
        
        if price and analysis:
            # حساب الأهداف
            h1, h2 = price * 1.03, price * 1.05
            d1, stop = price * 0.97, price * 0.94
            
            # التوصية الذكية
            if analysis['short'] == "صاعد 📈" and "+" in change:
                rec = "شراء قوي 🚀"
            elif analysis['short'] == "صاعد 📈":
                rec = "احتفاظ ✅"
            else:
                rec = "مراقبة / حياد ⚖️"

            st.markdown(f"""
            <div class="telegram-card">
                <div style="font-size: 20px; font-weight: bold;">💎 تقرير الأداء الفني لـ {ticker}</div>
                <div class="line"></div>
                💰 <b>السعر اللحظي:</b> <br>
                <span class="price-val">{price:.3f}</span> <small>{change}</small><br>
                📟 <b>مؤشر RSI:</b> {analysis['rsi']:.1f}
                <div class="line"></div>
                🧭 <b>تحليل الاتجاهات:</b><br>
                🔹 مدى قصير (20 يوم): <b>{analysis['short']}</b><br>
                🔹 مدى متوسط (50 يوم): <b>{analysis['mid']}</b><br>
                🔹 مدى طويل (200 يوم): <b>{analysis['long']}</b>
                <div class="line"></div>
                💧 <b>السيولة والنشاط:</b><br>
                قيمة تداول اليوم: {turnover}<br>
                📢 <b>التوصية: {rec}</b>
                <div class="line"></div>
                🚀 <b>مستويات المستهدفات:</b><br>
                🔷 هدف 1: {h1:.3f} | 🔷 هدف 2: {h2:.3f}
                <div class="line"></div>
                🛡️ <b>الدعم ووقف الخسارة:</b><br>
                🔶 دعم: {d1:.3f} | 🛑 <b>وقف: {stop:.3f}</b>
            </div>
            """, unsafe_allow_html=True)
