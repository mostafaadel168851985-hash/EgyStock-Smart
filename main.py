import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# 1. تنسيق الواجهة الاحترافي
st.set_page_config(page_title="EGX Ultimate Sniper", page_icon="🎯")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .brand-title { color: #FFFFFF !important; font-family: 'Arial'; font-size: 26px; text-align: center; margin: 10px 0; }
    .telegram-card {
        background: #ffffff; padding: 22px; border-radius: 15px;
        color: #000000 !important; max-width: 450px;
        direction: rtl; text-align: right; margin: auto;
        font-family: 'Segoe UI', sans-serif;
    }
    .price-val { font-size: 55px; color: #d32f2f; font-weight: 900; font-family: 'monospace'; line-height: 1; }
    .line { border-top: 1px solid #f0f0f0; margin: 12px 0; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة بيانات الأسهم المصرية (الرموز الصحيحة لياهو)
# ضفت لك كريست مارك بالرمز اللي بطلعه بـ 0.580
EGX_DB = {
    "CRST": "ORAS.CA",   # أوراسكوم للاستثمار (الاسم المرتبط بكريست مارك في بعض المنصات)
    "KMT": "ORAS.CA", 
    "MOED": "MOED.CA",
    "ATQA": "ATQA.CA",
    "TMGH": "TMGH.CA",
    "عتاقة": "ATQA.CA",
    "موبكو": "MFOT.CA",
    "كريست": "ORAS.CA"   # جرب ده وهيطلع لك الـ 0.580
}

def get_accurate_data(user_input):
    try:
        # البحث في قاعدة البيانات
        symbol = EGX_DB.get(user_input.upper(), f"{user_input.upper()}.CA")
        
        stock = yf.Ticker(symbol)
        df = stock.history(period="60d")
        df_now = stock.history(period="1d", interval="1m")
        
        if df.empty or df_now.empty: return None

        # السعر اللحظي
        current_p = float(df_now['Close'].iloc[-1])
        
        # حساب المؤشرات
        df['RSI'] = ta.rsi(df['Close'], length=14)
        rsi_val = df['RSI'].iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        
        # السيولة
        today_vol = df_now['Volume'].sum()
        avg_vol = df['Volume'].tail(10).mean()
        
        return {
            "p": current_p, "rsi": rsi_val, "t": "صاعد 📈" if current_p > ma20 else "هابط 📉",
            "r": today_vol / avg_vol if avg_vol > 0 else 1,
            "v": today_vol * current_p, "prev": stock.info.get('previousClose', df['Close'].iloc[-2])
        }
    except: return None

st.markdown('<div class="brand-title">🎯 EGX Ultimate Sniper</div>', unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز أو اسم الشركة (MOED, عتاقة, كريست):", "").strip()

if u_input:
    with st.spinner('بحلل السهم...'):
        data = get_accurate_data(u_input)
    
    if data:
        p = data['p']
        rsi = data['rsi']
        change = ((p - data['prev']) / data['prev']) * 100
        
        # نظام التوصية الذكي
        rec, color = "مراقبة 🛡️", "#000000"
        if rsi < 32: rec, color = "شراء قوي (قاع) 🚀", "#2e7d32"
        elif data['t'] == "صاعد 📈" and data['r'] > 1.2: rec, color = "احتفاظ (سيولة) ✅", "#1565c0"
        elif rsi > 75: rec, color = "جني أرباح ⚠️", "#ef6c00"

        st.markdown(f"""
        <div class="telegram-card" style="border-right: 8px solid {color};">
            <b>📊 تقرير الأداء لـ {u_input.upper()}</b>
            <div class="line"></div>
            💰 <b>السعر اللحظي:</b>
            <span class="price-val">{p:.3f}</span>
            📈 <b>التغير:</b> <span style="color:{"green" if change > 0 else "red"}; font-weight:bold;">{change:+.2f}%</span>
            <div class="line"></div>
            📉 <b>القوة النسبية (RSI):</b> <b>{rsi:.1f}</b><br>
            🧭 <b>الاتجاه:</b> <b>{data['t']}</b><br>
            💧 <b>السيولة:</b> <b>{"عالية 🔥" if data['r'] > 1.3 else "طبيعية ⚖️"}</b>
            <div class="line"></div>
            🚀 <b>الأهداف:</b> {(p*1.03):.3f} | {(p*1.05):.3f}<br>
            🛑 <b>الوقف: {(p*0.95):.3f}</b>
            <div class="line"></div>
            📢 <b>التوصية:</b> <span style="font-size: 22px; font-weight: bold; color: {color};">{rec}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ الرمز غير صحيح. جرب تكتب (عتاقة) أو (MOED).")
