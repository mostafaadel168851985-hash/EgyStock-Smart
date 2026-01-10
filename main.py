import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper v20", layout="centered")

# --- CSS التنسيق الموحد ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        max-width: 450px; margin: 10px auto;
    }
    .separator { border-top: 1px solid #444; margin: 12px 0; }
    .price-large { font-weight: bold; font-size: 28px; color: #4cd964; text-align: center; display: block; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 18px; }
    .info-line { margin: 8px 0; font-size: 16px; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 12px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_auto_data(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        df = yf.Ticker(symbol).history(period="150d")
        if df.empty: return None
        p = df['Close'].iloc[-1]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        vol = (df['Volume'].iloc[-1] * p) / 1_000_000
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma100 = df['Close'].rolling(100).mean().iloc[-1]
        return {"p": p, "rsi": rsi, "vol": vol, 
                "s_t": "صاعد 🟢" if p > ma20 else "هابط 🔴", 
                "m_t": "صاعد 🟢" if p > ma50 else "هابط 🔴", 
                "l_t": "صاعد 🟢" if p > ma100 else "هابط 🔴"}
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)

# حجر الزاوية: رمز السهم هو اللي بيتحكم في تصفير الخانات
u_input = st.text_input("🔍 ادخل الرمز (مثلاً ATQA):").upper()

# --- 1. عرض الكارت الآلي ---
if u_input:
    d = get_auto_data(u_input)
    if d:
        st.markdown(f"""
        <div class="report-card">
            <div style="text-align:center; font-size:20px;">💎 التحليل الشامل لـ {u_input} (آلي)</div>
            <div class="separator"></div>
            <span class="price-large">{d['p']:.3f}</span>
            <div class="info-line">📟 مؤشر RSI: <b>{d['rsi']:.1f}</b> | 💧 السيولة: <b>{d['vol']:.1f}M</b></div>
            <div class="separator"></div>
            <div class="label-blue">🔍 اتجاهات السهم:</div>
            <div class="info-line">📈 قصير: {d['s_t']} | متوسط: {d['m_t']}</div>
            <div class="info-line">📉 طويل المدى: {d['l_t']}</div>
            <div class="separator"></div>
            <div class="label-blue">🚀 مستويات الأهداف:</div>
            <div class="info-line">🔹 هدف 1: <b>{d['p']*1.025:.3f}</b> | 🔹 هدف 2: <b>{d['p']*1.05:.3f}</b></div>
            <div class="separator"></div>
            <div class="label-blue">🛡️ مستويات الدعم:</div>
            <div class="info-line">🔸 دعم 1: <b>{d['p']*0.975:.3f}</b> | 🔸 دعم 2: <b>{d['p']*0.95:.3f}</b></div>
            <div class="info-line" style="color:#ff3b30; text-align:center; font-weight:bold;">🛑 وقف خسارة: {d['p']*0.94:.3f}</div>
            <a href="https://wa.me/?text=تحليل {u_input}: {d['p']:.3f}" class="wa-button">🚀 مشاركة التقرير الآلي</a>
        </div>
        """, unsafe_allow_html=True)

# --- 2. لوحة الإدخال اليدوي مع خاصية التصفير الذكي ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة القناص اليدوية</h3>", unsafe_allow_html=True)

# ربطنا الـ key بـ u_input عشان الخانات تفضى لو السهم اتغير
col1, col2, col3 = st.columns(3)
with col1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key=f"v1_{u_input}")
with col2: m_h = st.number_input("🔝 أعلى سعر:", format="%.3f", key=f"v2_{u_input}")
with col3: m_l = st.number_input("📉 أقل سعر:", format="%.3f", key=f"v3_{u_input}")

col4, col5, col6 = st.columns(3)
with col4: m_cl = st.number_input("↩️ إغلاق أمس:", format="%.3f", key=f"v4_{u_input}")
with col5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key=f"v5_{u_input}")
with col6: m_v = st.number_input("💧 قيمة التداول (M):", format="%.2f", key=f"v6_{u_input}")

if m_p > 0 and m_h > 0:
    piv = (m_h + m_l + m_p) / 3
    r1, r2 = (2 * piv) - m_l, piv + (m_h - m_l)
    s1, s2 = (2 * piv) - m_h, piv - (m_h - m_l)
    trend = "صاعد 🟢" if m_p > m_cl else "هابط 🔴"

    st.markdown(f"""
    <div class="report-card" style="border-right: 8px solid #3498db;">
        <div style="text-align:center; font-size:20px; color:#3498db;">🛠️ التقرير اليدوي لـ {u_input if u_input else 'السهم'}</div>
        <div class="separator"></div>
        <span class="price-large">{m_p:.3f}</span>
        <div class="info-line">📍 نقطة الارتكاز: <b>{piv:.3f}</b> | 💧 السيولة: <b>{m_v:.1f}M</b></div>
        <div class="separator"></div>
        <div class="label-blue">🔍 تحليل الحالة:</div>
        <div class="info-line">📈 الاتجاه الحالي: {trend}</div>
        <div class="info-line">🏢 هدف المستثمر: <b>{m_p*1.20:.3f}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🚀 مستويات الأهداف (المقاومة):</div>
        <div class="info-line">🔹 هدف 1: <b>{r1:.3f}</b> | 🔹 هدف 2: <b>{r2:.3f}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🛡️ مستويات الدعم:</div>
        <div class="info-line">🔸 دعم 1: <b>{s1:.3f}</b> | 🔸 دعم 2: <b>{s2:.3f}</b></div>
        <div class="info-line" style="color:#ff3b30; text-align:center; font-weight:bold;">🛑 وقف خسارة: {s1*0.98:.3f}</div>
        <a href="https://wa.me/?text=تحليل يدوي {u_input}: {m_p:.3f}" class="wa-button">🚀 مشاركة التقرير اليدوي</a>
    </div>
    """, unsafe_allow_html=True)

st.caption("EGX Ultimate Sniper v20.0 | Smart Reset Enabled")
