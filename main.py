import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعداد الصفحة
st.set_page_config(page_title="EGX Sniper Pro", page_icon="🎯", layout="centered")

# --- تنسيق الواجهة (إصلاح الأخطاء السابقة) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    
    /* الكارت الأبيض - نظيف تماماً */
    .report-card { 
        background: white; padding: 25px; border-radius: 15px; 
        color: black; direction: rtl; text-align: right; 
        margin-bottom: 20px; border-top: 8px solid #1a73e8;
    }
    
    .price-val { font-size: 50px; color: #d32f2f; font-weight: 900; font-family: monospace; }
    
    /* لوحة التحليل اليدوي - منورة */
    .manual-header {
        background: white; color: black; padding: 15px; 
        border-radius: 10px; text-align: center; margin: 20px 0;
        font-weight: bold; font-size: 20px; border: 2px solid #1a73e8;
    }
    
    .manual-box {
        background: #111; padding: 20px; border-radius: 12px; 
        border: 1px solid #333; color: white;
    }
    
    .whatsapp-container {
        border: 2px solid #25d366; padding: 15px; border-radius: 10px;
        background: #050505; color: #25d366; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- الوظيفة الآلية ---
def get_auto(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        df = stock.history(period="100d")
        if df.empty: return None
        p = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        return {"p": p, "prev": prev, "rsi": rsi, "vol": (df['Volume'].iloc[-1]*p)/1_000_000}
    except: return None

# --- واجهة المستخدم ---
st.markdown("<h1 style='text-align:center; color:white;'>💎 رادار البورصة الذكي</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (ATQA, MOED, CRST):", "").strip().upper()

if u_input:
    auto = get_auto(u_input)
    final_report = ""

    # 1. عرض التقرير الآلي (لو متاح)
    if auto:
        p = auto['p']
        change = ((p - auto['prev']) / auto['prev']) * 100
        st.markdown(f"""
        <div class="report-card">
            <h2 style="margin:0;">📊 تقرير {u_input} اللحظي</h2>
            <div class="price-val">{p:.3f}</div>
            <b style="color:{'green' if change > 0 else 'red'};">{change:+.2f}%</b>
            <p>RSI: {auto['rsi']:.1f} | سيولة: {auto['vol']:.2f}M</p>
            <hr>
            <b>🚀 الأهداف:</b> {p*1.03:.3f} | {p*1.06:.3f}<br>
            <b>🛡️ الدعوم:</b> {p*0.97:.3f} | {p*0.95:.3f}<br>
            <b>🛑 الوقف:</b> {p*0.94:.3f}
        </div>
        """, unsafe_allow_html=True)
        final_report = f"تحليل {u_input}:\nسعر: {p:.3f}\nهدف: {p*1.03:.3f}\nوقف: {p*0.94:.3f}"

    # 2. لوحة التحليل اليدوي (منورة أبيض)
    st.markdown(f'<div class="manual-header">🛠️ لوحة القناص اليدوية لـ {u_input}</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="manual-box">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: m_p = st.number_input("السعر الآن:", format="%.3f", key="n1")
        with col2: m_h = st.number_input("أعلى سعر اليوم:", format="%.3f", key="n2")
        with col3: m_l = st.number_input("أقل سعر اليوم:", format="%.3f", key="n3")
        
        col4, col5, col6 = st.columns(3)
        with col4: m_prev = st.number_input("إغلاق أمس:", format="%.3f", key="n4")
        with col5: m_mh = st.number_input("أعلى سعر شهر:", format="%.3f", key="n5")
        with col6: m_vol = st.number_input("سيولة اليوم (M):", format="%.2f", key="n6")
        st.markdown('</div>', unsafe_allow_html=True)

        if m_p > 0 and m_h > 0:
            # معادلات الارتكاز (Pivot)
            pivot = (m_h + m_l + m_p) / 3
            r1 = (2 * pivot) - m_l
            s1 = (2 * pivot) - m_h
            
            st.markdown(f"""
            <div class="report-card" style="border-top-color:#00c853;">
                <h2 style="margin:0;">✅ نتيجة التحليل اليدوي</h2>
                <div class="price-val">{m_p:.3f}</div>
                <hr>
                <b>📍 نقطة الارتكاز:</b> {pivot:.3f}<br>
                <b>🎯 هدف المضارب:</b> {r1:.3f}<br>
                <b>🛡️ دعم المضارب:</b> {s1:.3f}<br>
                <p style="color:blue;">(السهم إيجابي طول ما هو فوق الارتكاز)</p>
            </div>
            """, unsafe_allow_html=True)
            final_report = f"تحليل يديوي {u_input}:\nسعر: {m_p:.3f}\nهدف: {r1:.3f}\nدعم: {s1:.3f}\nارتكاز: {pivot:.3f}"

    # 3. صندوق النسخ للواتساب
    if final_report:
        st.markdown(f"""
        <div class="whatsapp-container">
            <b>📱 التقرير جاهز للنسخ:</b><br><br>
            {final_report.replace('\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)
        st.button("انسخ النص وشاركه 🚀")

st.caption("EGX Smart Sniper v5.0 | مصطفى عادل")
