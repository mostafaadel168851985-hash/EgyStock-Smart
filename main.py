import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Analyst", page_icon="💎", layout="centered")

# --- تنسيق الواجهة (ستايل التليجرام) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .telegram-card {
        background: white; padding: 20px; border-radius: 10px;
        color: black; direction: rtl; text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        border-right: 5px solid #1a73e8; margin-bottom: 20px;
    }
    .manual-section {
        background: #111; padding: 15px; border-radius: 10px;
        border: 1px dashed #444; color: white; margin-top: 10px;
    }
    .line { border-top: 2px solid #eee; margin: 10px 0; }
    h4 { margin: 0; color: #1a73e8; }
    </style>
    """, unsafe_allow_html=True)

# --- دالة التحليل الفني المتقدم ---
def get_full_analysis(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        df = stock.history(period="150d") # سحب فترة كافية للمتوسطات
        if df.empty: return None
        
        # السعر والمؤشرات
        p = df['Close'].iloc[-1]
        df['RSI'] = ta.rsi(df['Close'], length=14)
        rsi = df['RSI'].iloc[-1]
        
        # الاتجاهات
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma100 = df['Close'].rolling(100).mean().iloc[-1]
        
        trend_s = "صاعد 🟢" if p > ma10 else "هابط 🔴"
        trend_m = "صاعد 🟢" if p > ma50 else "هابط 🔴"
        trend_l = "صاعد 🟢" if p > ma100 else "هابط 🔴"
        
        return {
            "p": p, "rsi": rsi, "ts": trend_s, "tm": trend_m, "tl": trend_l,
            "prev": stock.info.get('previousClose', df['Close'].iloc[-2]),
            "vol": (df['Volume'].iloc[-1] * p) / 1_000_000
        }
    except: return None

# --- واجهة البرنامج ---
st.markdown("<h2 style='text-align:center; color:white;'>💎 المحلل الشامل للبورصة</h2>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثل ATQA أو MOED):", "").strip().upper()

if u_input:
    auto_data = get_full_analysis(u_input)
    
    # 1. عرض التحليل الآلي (إذا وجد)
    if auto_data:
        st.markdown(f"""
        <div class="telegram-card">
            <h4>💎 التحليل الشامل لـ {u_input}</h4>
            <div class="line"></div>
            💰 <b>السعر المعتمد:</b> {auto_data['p']:.2f}<br>
            📟 <b>مؤشر RSI:</b> {auto_data['rsi']:.1f}<br>
            💧 <b>نبض السيولة:</b> {'طبيعية ⚖️' if auto_data['vol'] < 5 else 'عالية 🔥'}<br>
            📢 <b>التوصية:</b> {'مراقبة 🛡️' if 40 < auto_data['rsi'] < 60 else 'فرصة ✨'}<br>
            <div class="line"></div>
            🔍 <b>الاتجاهات الفنية:</b><br>
            • مدى قصير: <b>{auto_data['ts']}</b><br>
            • مدى متوسط: <b>{auto_data['tm']}</b><br>
            • مدى طويل: <b>{auto_data['tl']}</b><br>
            <div class="line"></div>
            🚀 <b>مستويات المقاومة:</b><br>
            • هدف 1: {auto_data['p']*1.03:.2f} 🔷<br>
            • هدف 2: {auto_data['p']*1.06:.2f} 🔷<br>
            <div class="line"></div>
            🛑 <b>وقف الخسارة:</b> {auto_data['p']*0.96:.2f} 🛑
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ الرمز {u_input} غير متاح آلياً. استخدم التحليل اليدوي أدناه.")

    # 2. قسم التحليل اليدوي (متاح دائماً أو كبديل)
    with st.expander("🛠️ لوحة التحليل اليدوي / إضافة بيانات خاصة", expanded=not auto_data):
        st.markdown("<p style='color:white;'>استخدم هذا القسم إذا أردت تعديل الأرقام يدوياً لسهم مثل كريست مارك:</p>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: m_price = st.number_input("السعر الآن:", format="%.3f")
        with c2: m_high = st.number_input("أعلى سعر:", format="%.3f")
        with c3: m_low = st.number_input("أقل سعر:", format="%.3f")
        
        st.write("📊 **إدخال السيولة (بالمليون):**")
        v1, v2 = st.columns(2)
        with v1: v_today = st.number_input("سيولة اليوم:", format="%.2f")
        with v2: v_avg = st.number_input("متوسط الشهر:", format="%.2f")

        if m_price > 0:
            pivot = (m_price + m_high + m_low) / 3
            st.markdown(f"""
            <div class="telegram-card" style="border-right-color: #00c853;">
                <h4>🛠️ تقرير يدوي لـ {u_input}</h4>
                <div class="line"></div>
                💰 <b>السعر الحالي:</b> {m_price:.3f}<br>
                💧 <b>حالة السيولة:</b> {'إيجابية 🔥' if v_today > v_avg else 'هادئة ⚖️'}<br>
                <div class="line"></div>
                🚀 <b>الأهداف الرقمية:</b><br>
                • هدف 1: {(2*pivot)-m_low:.3f} 🔷<br>
                • هدف 2: {pivot+(m_high-m_low):.3f} 🔷<br>
                <div class="line"></div>
                🛑 <b>دعم القوة (وقف):</b> {(2*pivot)-m_high:.3f} 🛑
            </div>
            """, unsafe_allow_html=True)

# --- تذكير بملف المتطلبات ---
# تأكد أن requirements.txt يحتوي على:
# streamlit
# yfinance
# pandas_ta
