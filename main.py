import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. إعدادات الصفحة Thndr Style
st.set_page_config(page_title="EgyStock PRO", layout="wide")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .telegram-card {
        background: #ffffff; padding: 20px; border-radius: 15px;
        color: #000000 !important; max-width: 500px; margin-bottom: 20px;
        direction: rtl; text-align: right; border: 1px solid #ddd;
    }
    .line { border-top: 2px solid #000; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# دالة ذكية لسحب البيانات مع حماية من الحظر
@st.cache_data(ttl=3600) # بيخزن البيانات ساعة عشان السيرفر ميعملش بلوك
def get_safe_data(ticker):
    sym = f"{ticker.strip().upper()}.CA"
    try:
        # بنطلب شهر واحد بس عشان الشارت يكون سريع وخفيف
        data = yf.download(sym, period="3mo", interval="1d", progress=False)
        if data.empty:
            data = yf.Ticker(sym).history(period="3mo")
        return data
    except:
        return pd.DataFrame()

ticker_input = st.text_input("🔍 اكتب رمز السهم (مثلاً TMGH, CRST, ATQA):", "ATQA").upper().strip()

if ticker_input:
    df = get_safe_data(ticker_input)
    
    if not df.empty and len(df) > 5:
        # الحسابات الفنية
        last_p = float(df['Close'].iloc[-1])
        avg_50 = float(df['Close'].rolling(min(len(df), 50)).mean().iloc[-1])
        
        # حساب RSI والسيولة
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_val = float(100 - (100 / (1 + rs.iloc[-1])))
        
        # الأهداف والدعوم
        h1, h2 = last_p * 1.03, last_p * 1.05
        d1, stop_loss = last_p * 0.97, last_p * 0.94

        # عرض الكارت الأبيض
        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 20px; font-weight: bold;">💎 التحليل الشامل لـ {ticker_input}</div>
            <div class="line"></div>
            💰 <b>السعر المعتمد:</b> {last_p:.2f}<br>
            📟 <b>مؤشر RSI:</b> {rsi_val:.1f}<br>
            💧 <b>نبض السيولة:</b> {"عالية 🔥" if rsi_val > 55 else "طبيعية ⚖️"}<br>
            📢 <b>التوصية:</b> {"احتفاظ ✅" if last_p > avg_50 else "مراقبة ⚖️"}
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            {"✅" if last_p > avg_50 else "⚠️"} السعر {"فوق" if last_p > avg_50 else "تحت"} متوسط 50<br>
            ⚠️ تحرك عرضي مستقر
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

        # رسم الشارت (الإصلاح الجذري)
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            increasing_line_color='#00E676', decreasing_line_color='#FF3D00'
        )])
        fig.update_layout(template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black', height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.error("⚠️ السيرفر مضغوط حالياً أو الرمز غير دقيق. (جرب مرة أخرى بعد دقيقة)")
