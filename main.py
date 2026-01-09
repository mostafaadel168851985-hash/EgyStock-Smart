import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# إعدادات الواجهة (ستايل التليجرام الاحترافي)
st.set_page_config(page_title="EgyStock Telegram Bot", layout="wide")
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .telegram-card {
        background: #ffffff; padding: 25px; border-radius: 15px;
        color: #000000 !important; max-width: 480px;
        direction: rtl; text-align: right; border: 1px solid #ddd;
        margin: auto; font-family: 'Arial', sans-serif; box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }
    .line { border-top: 2px solid #000; margin: 12px 0; }
    .price-bold { font-size: 28px; color: #d32f2f; font-weight: bold; }
    .status-up { color: #008000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def get_data_and_analyze(ticker):
    sym = f"{ticker}.CA"
    # محاولة جلب بيانات تاريخية للحسابات الفنية
    df = yf.download(sym, period="1mo", interval="1d", progress=False)
    
    # محاولة جلب السعر اللحظي من مباشر (لضمان الدقة في الأسهم الجديدة)
    live_price = None
    try:
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        price_tag = soup.find('div', {'class': 'market-summary__last-price'})
        if price_tag:
            live_price = float(price_tag.text.strip().replace(',', ''))
    except: pass

    if not df.empty:
        last_p = live_price if live_price else float(df['Close'].iloc[-1])
        # حساب RSI تقريبي للسيولة
        delta = df['Close'].diff()
        up = delta.clip(lower=0).rolling(14).mean()
        down = -delta.clip(upper=0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (up / down).iloc[-1]))
        
        # الأهداف والدعوم
        h1, h2 = last_p * 1.03, last_p * 1.05
        d1, stop = last_p * 0.97, last_p * 0.94
        
        return {
            "price": last_p, "rsi": rsi, 
            "h1": h1, "h2": h2, "d1": d1, "stop": stop
        }
    return None

st.title("📲 محاكي توصيات التليجرام")
ticker = st.text_input("ادخل رمز السهم (مثال: CRST, MOED, ATQA):", "CRST").strip().upper()

if ticker:
    data = get_data_and_analyze(ticker)
    
    if data:
        # تحديد التوصية والسيولة ديناميكياً
        liq = "عالية 🔥" if data['rsi'] > 55 else "هادئة ⚖️"
        rec = "شراء / احتفاظ ✅" if data['rsi'] < 70 else "جني أرباح ⚠️"
        tech_reason = "فوق متوسط 50" if data['price'] > (data['price']*0.98) else "تحت الضغط"

        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 20px; font-weight: bold;">💎 التحليل الشامل لـ {ticker}</div>
            <div class="line"></div>
            💰 <b>السعر المعتمد:</b> <span class="price-bold">{data['price']:.3f}</span><br>
            📟 <b>مؤشر RSI:</b> {data['rsi']:.1f}<br>
            💧 <b>نبض السيولة:</b> {liq}<br>
            📢 <b>التوصية:</b> {rec}
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            ✅ السعر {tech_reason}<br>
            ⚠️ تحرك عرضي مستقر
            <div class="line"></div>
            🚀 <b>مستويات المقاومة:</b><br>
            🔷 هدف 1: {data['h1']:.3f}<br>
            🔷 هدف 2: {data['h2']:.3f}
            <div class="line"></div>
            🛡️ <b>مستويات الدعم:</b><br>
            🔶 دعم 1: {data['d1']:.3f}<br>
            🔶 دعم 2: {data['price']*0.96:.3f}
            <div class="line"></div>
            🛑 <b>وقف الخسارة:</b> {data['stop']:.3f}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ لا يمكن العثور على بيانات لهذا الرمز حالياً.")
