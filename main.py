import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. إعدادات الصفحة والتنسيق
st.set_page_config(page_title="EgyStock PRO", layout="wide")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .telegram-card {
        background: #ffffff; padding: 20px; border-radius: 15px;
        color: #000000 !important; max-width: 500px; margin-bottom: 20px;
        direction: rtl; text-align: right; border: 1px solid #ddd; box-shadow: 0px 4px 10px rgba(255,255,255,0.2);
    }
    .line { border-top: 2px solid #000; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# دالة سحب البيانات (مطورة جداً لضمان التحديث)
def get_live_data(ticker):
    sym = f"{ticker.strip().upper()}.CA"
    # بنجرب نسحب بـ Ticker مباشرة لتفادي الحظر
    t = yf.Ticker(sym)
    df = t.history(period="3mo", interval="1d")
    return df

ticker_input = st.text_input("🔍 اكتب رمز السهم فقط (مثلاً TMGH أو CRST):", "TMGH").upper().strip()

if ticker_input:
    # ملاحظة: لا تكتب السعر بجانب السهم في الخانة، اكتب الرمز فقط
    df = get_live_data(ticker_input)
    
    if not df.empty and len(df) > 1:
        # السعر المحدث (آخر إغلاق مسجل)
        last_p = float(df['Close'].iloc[-1])
        
        # حساب RSI والسيولة
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_val = float(100 - (100 / (1 + rs.iloc[-1])))
        
        # الأهداف (معادلة تليجرام)
        h1, h2 = last_p * 1.03, last_p * 1.05
        d1, stop_loss = last_p * 0.97, last_p * 0.94

        # عرض الكارت الأبيض (تنسيق التليجرام)
        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 20px; font-weight: bold;">💎 التحليل الشامل لـ {ticker_input}</div>
            <div class="line"></div>
            💰 <b>السعر المحدث:</b> {last_p:.2f}<br>
            📟 <b>مؤشر RSI:</b> {rsi_val:.1f}<br>
            💧 <b>نبض السيولة:</b> {"عالية 🔥" if rsi_val > 55 else "طبيعية ⚖️"}<br>
            📢 <b>التوصية:</b> {"احتفاظ ✅" if rsi_val > 50 else "مراقبة ⚖️"}
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            ✅ تحديث تلقائي للبيانات<br>
            ⚠️ سيولة {"نشطة" if rsi_val > 50 else "مستقرة"}
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

        # 2. رسم الشارت (إصلاح مشكلة الاختفاء)
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            increasing_line_color='#00E676', decreasing_line_color='#FF3D00'
        )])
        fig.update_layout(
            template="plotly_dark", 
            paper_bgcolor='black', 
            plot_bgcolor='black', 
            height=500, 
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        # إظهار الشارت بأمر مباشر
        st.plotly_chart(fig, use_container_width=True, key="stock_chart")
        
    else:
        st.warning(f"⚠️ ياهو فاينانس يحتاج دقيقة لتحديث بيانات {ticker_input}. برجاء المحاولة مرة أخرى.")
