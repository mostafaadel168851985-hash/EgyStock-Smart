import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. إعدادات الصفحة
st.set_page_config(page_title="EgyStock PRO", layout="wide")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .telegram-card {
        background: #ffffff; padding: 20px; border-radius: 15px;
        color: #000000 !important; max-width: 500px;
        font-family: 'Arial', sans-serif; line-height: 1.6;
        border: 1px solid #ddd; direction: rtl; text-align: right;
    }
    .line { border-top: 2px solid #000; margin: 10px 0; }
    .neon-green { color: #008000 !important; font-weight: bold; }
    .neon-red { color: #ff0000 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

ticker_input = st.text_input("🔍 ابحث عن سهم (مثلاً TMGH, FWRY, CRST):", "TMGH").upper().strip()

def get_data(ticker):
    sym = f"{ticker}.CA"
    df = yf.download(sym, period="6mo", interval="1d", progress=False)
    if df.empty:
        df = yf.Ticker(sym).history(period="6mo")
    return df

if ticker_input:
    df = get_data(ticker_input)
    
    if not df.empty and len(df) > 20:
        last_p = float(df['Close'].iloc[-1])
        # حساب RSI بدقة للسيولة
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_val = float(100 - (100 / (1 + rs.iloc[-1])))
        
        # حساب المتوسطات للأسباب الفنية
        avg_50 = float(df['Close'].rolling(50).mean().iloc[-1])
        
        # مستويات الأهداف والدعم
        h1 = last_p * 1.03
        h2 = last_p * 1.05
        d1 = last_p * 0.97
        stop_loss = last_p * 0.94

        # تحديد نبض السيولة
        if rsi_val >= 60:
            liquidity = "عالية 🔥"
            liq_reason = "القوة النسبية (RSI) عالية"
        elif rsi_val <= 40:
            liquidity = "ضعيفة 🧊"
            liq_reason = "السهم في منطقة تشبع بيعي"
        else:
            liquidity = "طبيعية ⚖️"
            liq_reason = "تحرك عرضي مستقر"

        # التوصية
        if rsi_val > 50 and last_p > avg_50:
            signal = "احتفاظ / مراقبة ✅"
        else:
            signal = "مراقبة / حيادي ⚖️"

        # عرض كارت التليجرام
        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 20px; font-weight: bold;">💎 التحليل الشامل لـ {ticker_input}</div>
            <div class="line"></div>
            💰 <b>السعر المعتمد:</b> {last_p:.2f}<br>
            📟 <b>مؤشر RSI:</b> {rsi_val:.1f}<br>
            💧 <b>نبض السيولة:</b> {liquidity}<br>
            📢 <b>التوصية:</b> {signal}
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            {"✅" if last_p > avg_50 else "❌"} السعر {"فوق" if last_p > avg_50 else "تحت"} متوسط 50<br>
            ⚠️ {liq_reason}
            <div class="line"></div>
            🚀 <b>مستويات المقاومة:</b><br>
            🔷 هدف 1: {h1:.2f}<br>
            🔷 هدف 2: {h2:.2f}
            <div class="line"></div>
            🛡️ <b>مستويات الدعم:</b><br>
            🔶 دعم 1: {d1:.2f}<br>
            🛑 <b>وقف الخسارة:</b> {stop_loss:.2f}
        </div>
        """, unsafe_allow_html=True)

        # الشارت
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            increasing_line_color='#00E676', decreasing_line_color='#FF3D00'
        )])
        fig.update_layout(template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black', height=400, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
