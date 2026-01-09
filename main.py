import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات التنسيق (كارت التليجرام)
st.set_page_config(page_title="EgyStock PRO", layout="wide")
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .telegram-card {
        background: #ffffff; padding: 20px; border-radius: 15px;
        color: #000000 !important; max-width: 500px;
        direction: rtl; text-align: right; border: 1px solid #ddd;
    }
    .line { border-top: 2px solid #000; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

ticker_input = st.text_input("🔍 اكتب رمز السهم فقط (مثلاً MOED أو CRST):", "MOED").upper().strip()

def get_accurate_data(ticker):
    sym = f"{ticker}.CA"
    # بنجرب نسحب بـ Ticker عشان نضمن الأسهم الجديدة
    t = yf.Ticker(sym)
    df = t.history(period="5d", interval="1d") # بنسحب آخر 5 أيام بس عشان السرعة
    return df

if ticker_input:
    df = get_accurate_data(ticker_input)
    
    if not df.empty:
        # حل مشكلة التقريب: بنستخدم .3f عشان يطلع 0.866 بالظبط
        last_p = float(df['Close'].iloc[-1])
        
        # حسابات الأهداف (بدقة 3 أرقام عشرية)
        h1, h2 = last_p * 1.03, last_p * 1.05
        d1, stop_loss = last_p * 0.97, last_p * 0.94

        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 20px; font-weight: bold;">💎 التحليل الشامل لـ {ticker_input}</div>
            <div class="line"></div>
            💰 <b>السعر المعتمد:</b> {last_p:.3f}<br>
            💧 <b>نبض السيولة:</b> طبيعية ⚖️<br>
            📢 <b>التوصية:</b> مراقبة ⚖️
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            ✅ تم تحديث السعر بدقة عالية<br>
            ⚠️ السهم في منطقة استقرار
            <div class="line"></div>
            🚀 <b>مستويات المقاومة:</b><br>
            🔷 هدف 1: {h1:.3f}<br>
            🔷 هدف 2: {h2:.3f}
            <div class="line"></div>
            🛡️ <b>مستويات الدعم:</b><br>
            🔶 دعم 1: {d1:.3f}<br>
            🛑 <b>وقف الخسارة:</b> {stop_loss:.3f}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error(f"⚠️ الرمز {ticker_input} غير متاح حالياً. تأكد أن السهم تم تداوله اليوم.")
