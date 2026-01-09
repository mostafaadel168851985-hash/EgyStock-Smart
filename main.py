import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعداد الصفحة
st.set_page_config(page_title="EGX Pro Sniper v6", page_icon="🎯", layout="centered")

# --- التنسيق البصري النهائي (إصلاح كل العيوب) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    
    /* الكارت الأبيض الشامل */
    .report-card { 
        background: white; padding: 25px; border-radius: 15px; 
        color: black; direction: rtl; text-align: right; 
        margin-bottom: 20px; border-top: 8px solid #1a73e8;
    }
    
    .price-big { font-size: 55px; color: #d32f2f; font-weight: 900; font-family: monospace; line-height: 1; }
    
    /* إبراز عناوين الإدخال اليدوي */
    label { 
        color: white !important; 
        font-size: 18px !important; 
        font-weight: bold !important; 
        text-shadow: 1px 1px 2px black;
    }

    /* عنوان لوحة القناص اليدوية */
    .manual-header-bright {
        background: white; color: #1a73e8; padding: 15px; 
        border-radius: 12px; text-align: center; margin: 25px 0;
        font-weight: 900; font-size: 22px; border: 4px solid #1a73e8;
    }
    
    .whatsapp-btn {
        background-color: #25d366; color: white; padding: 15px;
        border-radius: 10px; text-align: center; font-weight: bold;
        margin-top: 20px; border: none; width: 100%; display: block;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- وظائف التحليل الآلي ---
def get_analysis(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        df = stock.history(period="150d")
        if df.empty: return None
        
        p = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        
        # حساب الاتجاهات
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        trend = "صاعد 🟢" if p > ma50 else "هابط 🔴"
        advice = "شراء / احتفاظ ✅" if rsi < 65 and p > ma20 else "مراقبة / حذر ⚠️"
        
        return {
            "p": p, "prev": prev, "rsi": rsi, 
            "vol": (df['Volume'].iloc[-1]*p)/1_000_000,
            "trend": trend, "advice": advice
        }
    except: return None

# --- واجهة البرنامج ---
st.markdown("<h1 style='text-align:center; color:white;'>🌊 رادار السيولة والقناص الرقمي</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل رمز السهم (مثلاً TMGH, MOED, CRST):", "").strip().upper()

if u_input:
    auto_data = get_analysis(u_input)
    msg_to_share = ""

    # 1. التقرير الآلي
    if auto_data:
        p = auto_data['p']
        change = ((p - auto_data['prev']) / auto_data['prev']) * 100
        st.markdown(f"""
        <div class="report-card">
            <h2 style="margin:0;">💎 التقرير الشامل لـ {u_input}</h2>
            <div class="price-big">{p:.3f}</div>
            <b style="color:{'green' if change > 0 else 'red'}; font-size:20px;">{change:+.2f}%</b>
            <p>RSI: {auto_data['rsi']:.1f} | سيولة الجلسة: {auto_data['vol']:.2f}M</p>
            <hr>
            <b>🔍 الاتجاه العام:</b> {auto_data['trend']}<br>
            <b>📢 التوصية:</b> {auto_data['advice']}<br>
            <hr>
            <b>🚀 الأهداف:</b> {p*1.03:.3f} | {p*1.06:.3f}<br>
            <b>🛡️ الدعوم:</b> {p*0.97:.3f} | {p*0.95:.3f}<br>
            <b>🛑 وقف الخسارة:</b> {p*0.94:.3f}
        </div>
        """, unsafe_allow_html=True)
        msg_to_share = f"🎯 تحليل {u_input}:\n💰 السعر: {p:.3f}\n📈 الاتجاه: {auto_data['trend']}\n🚀 الأهداف: {p*1.03:.3f} - {p*1.06:.3f}\n🛑 الوقف: {p*0.94:.3f}"

    # 2. لوحة القناص اليدوية (العناوين بارزة جداً)
    st.markdown(f'<div class="manual-header-bright">🛠️ لوحة القناص اليدوية لـ {u_input}</div>', unsafe_allow_html=True)
    
    with st.container():
        # استخدام columns لتنظيم الخانات بشكل بارز
        c1, c2, c3 = st.columns(3)
        with c1: m_price = st.number_input("💵 السعر الآن:", format="%.3f", key="v1")
        with c2: m_high = st.number_input("🔝 أعلى سعر اليوم:", format="%.3f", key="v2")
        with c3: m_low = st.number_input("📉 أقل سعر اليوم:", format="%.3f", key="v3")
        
        c4, c5, c6 = st.columns(3)
        with c4: m_close = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="v4")
        with c5: m_mhigh = st.number_input("🗓️ أعلى سعر شهر:", format="%.3f", key="v5")
        with c6: m_v = st.number_input("💧 سيولة اليوم (M):", format="%.2f", key="v6")

        if m_price > 0 and m_high > 0:
            # حسابات احترافية للمضارب والمستثمر
            pivot = (m_high + m_low + m_price) / 3
            r1 = (2 * pivot) - m_low
            s1 = (2 * pivot) - m_high
            inv_target = m_mhigh * 1.10 # هدف استثماري 10% فوق القمة الشهرية
            
            st.markdown(f"""
            <div class="report-card" style="border-top-color: #00c853;">
                <h2 style="margin:0;">✅ نتيجة التحليل اليدوي</h2>
                <div class="price-big">{m_price:.3f}</div>
                <hr>
                <b>🎯 هدف المضارب اللحظي:</b> {r1:.3f}<br>
                <b>🛡️ دعم المضارب القوي:</b> {s1:.3f}<br>
                <b>📍 نقطة الارتكاز (Pivot):</b> {pivot:.3f}<br>
                <hr>
                <b>🏢 هدف المستثمر (متوسط):</b> {inv_target:.3f}<br>
                <b>📊 حالة السيولة:</b> {"قوية 🔥" if m_v > 5 else "هادئة ⚖️"}
            </div>
            """, unsafe_allow_html=True)
            msg_to_share = f"🛠️ تحليل يدوي {u_input}:\n💰 السعر: {m_price:.3f}\n🎯 هدف لحظي: {r1:.3f}\n🏢 هدف مستثمر: {inv_target:.3f}\n📍 الارتكاز: {pivot:.3f}"

    # 3. زر الواتساب (يظهر في النهاية)
    if msg_to_share:
        st.write("---")
        st.markdown(f'<div style="color:white; font-weight:bold; margin-bottom:10px;">📱 شارك التقرير على واتساب:</div>', unsafe_allow_html=True)
        st.text_area("انسخ هذا النص:", msg_to_share, height=120)
        # رابط واتساب مباشر (اختياري)
        whatsapp_url = f"https://wa.me/?text={msg_to_share.replace(' ', '%20').replace('', '%0A')}"
        st.markdown(f'<a href="{whatsapp_url}" class="whatsapp-btn">🚀 إرسال مباشر لواتساب</a>', unsafe_allow_html=True)

st.caption("EGX Ultimate Sniper v6.0 | مصطفى عادل 2026")
