import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper", layout="centered")

# --- CSS (التصميم الموحد للكارت الآلي واليدوي) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .whatsapp-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        max-width: 450px; margin: 10px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .manual-header { border-bottom: 2px solid #3498db; margin-bottom: 15px; padding-bottom: 5px; color: #3498db; font-weight: bold; }
    .price-val { font-weight: bold; font-family: monospace; font-size: 19px; color: #4cd964; }
    .info-line { font-size: 17px; margin: 10px 0; }
    .wa-link {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 15px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin: 20px auto; max-width: 280px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.05);} 100% {transform: scale(1);} }
    </style>
    """, unsafe_allow_html=True)

# دالة لجلب البيانات الآلية
def get_live_data(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        df = stock.history(period="100d")
        if df.empty: return None
        p = df['Close'].iloc[-1]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        vol_m = (df['Volume'].iloc[-1] * p) / 1_000_000
        return {"p": p, "rsi": rsi, "vol": vol_m}
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المحترف</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً ATQA):").upper()

# --- 1. القسم الآلي ---
if u_input:
    d = get_live_data(u_input)
    if d:
        p = d['p']
        st.markdown(f"""<div class="whatsapp-card">
            <div style="font-size:20px; text-align:center;">💎 تقرير {u_input} (آلي)</div>
            <hr>
            <div class="info-line">💰 السعر: <span class="price-val">{p:.3f}</span></div>
            <div class="info-line">📟 مؤشر RSI: <b>{d['rsi']:.1f}</b></div>
            <div class="info-line">🚀 أهداف: <b>{p*1.025:.3f} | {p*1.05:.3f}</b></div>
            <div class="info-line">🛡️ دعوم: <b>{p*0.975:.3f} | {p*0.95:.3f}</b></div>
            <div class="info-line">🛑 وقف: <span style="color:#ff3b30;">{p*0.94:.3f}</span></div>
        </div>""", unsafe_allow_html=True)
        msg = f"💎 تحليل {u_input}%0A💰 السعر: {p:.3f}%0A🚀 أهداف: {p*1.025:.3f}%0A🛑 وقف: {p*0.94:.3f}"
        st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank" class="wa-link">🚀 مشاركة التقرير الآلي</a>', unsafe_allow_html=True)

# --- 2. لوحة القناص اليدوية (الإصلاح الجذري) ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة التحليل اليدوي (مضارب + مستثمر)</h3>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key="p1")
with c2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="p2")
with c3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f", key="p3")

c4, c5, c6 = st.columns(3)
with c4: m_cl = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="p4")
with c5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="p5")
with c6: m_v = st.number_input("💧 سيولة اليوم:", key="p6")

# حساب وعرض النتائج اليدوية في كارت منفصل
if m_p > 0 and m_h > 0 and m_l > 0:
    # معادلات البيفوت (Pivot Points)
    piv = (m_h + m_l + m_p) / 3
    r1 = (2 * piv) - m_l
    r2 = piv + (m_h - m_l)
    s1 = (2 * piv) - m_h
    s2 = piv - (m_h - m_l)
    stop_loss = s1 * 0.99 # وقف الخسارة تحت الدعم الأول بـ 1%

    st.markdown(f"""
    <div class="whatsapp-card">
        <div class="manual-header">🛠️ نتائج التحليل اليدوي لـ {u_input if u_input else 'هذا السهم'}</div>
        <div class="info-line">📍 نقطة الارتكاز: <span style="color:#3498db; font-weight:bold;">{piv:.3f}</span></div>
        <div class="info-line">🚀 أهدافك (المقاومة):</div>
        <div class="info-line">🔹 هدف 1: <span class="price-val">{r1:.3f}</span></div>
        <div class="info-line">🔹 هدف 2: <span class="price-val">{r2:.3f}</span></div>
        <hr style="opacity:0.3">
        <div class="info-line">🛡️ مستويات الحماية (الدعم):</div>
        <div class="info-line">🔸 دعم 1: <b>{s1:.3f}</b></div>
        <div class="info-line">🔸 دعم 2: <b>{s2:.3f}</b></div>
        <div class="info-line">🛑 وقف خسارة مقترح: <span style="color:#ff3b30; font-weight:bold;">{stop_loss:.3f}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # زر واتساب للبيانات اليدوية
    m_msg = f"🛠️ تحليل يدوي {u_input}%0A💰 السعر: {m_p:.3f}%0A📍 الارتكاز: {piv:.3f}%0A🚀 أهداف: {r1:.3f} - {r2:.3f}%0A🛑 وقف: {stop_loss:.3f}"
    st.markdown(f'<a href="https://wa.me/?text={m_msg}" target="_blank" class="wa-link">🚀 مشاركة التحليل اليدوي</a>', unsafe_allow_html=True)

st.caption("EGX Ultimate Sniper v13.0 | M. Adel Custom Build")
