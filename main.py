import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper v21", layout="centered")

# --- CSS التنسيق الموحد ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        max-width: 450px; margin: 15px auto;
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
        return {"p": p, "rsi": rsi, "vol": vol, "trend": "صاعد 🟢" if p > ma20 else "هابط 🔴"}
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً ATQA):").upper()

# --- 1. التقرير الآلي ---
if u_input:
    d = get_auto_data(u_input)
    if d:
        r1, r2 = d['p']*1.025, d['p']*1.05
        s1, s2 = d['p']*0.975, d['p']*0.95
        stop = d['p']*0.94
        
        st.markdown(f"""
        <div class="report-card">
            <div style="text-align:center; font-size:20px;">💎 تحليل {u_input} (آلي)</div>
            <div class="separator"></div>
            <span class="price-large">{d['p']:.3f}</span>
            <div class="info-line">📟 RSI: {d['rsi']:.1f} | 💧 السيولة: {d['vol']:.1f}M</div>
            <div class="separator"></div>
            <div class="label-blue">🚀 الأهداف: {r1:.3f} | {r2:.3f}</div>
            <div class="label-blue">🛡️ الدعوم: {s1:.3f} | {s2:.3f}</div>
            <div style="color:#ff3b30; font-weight:bold;">🛑 وقف خسارة: {stop:.3f}</div>
        """, unsafe_allow_html=True)
        
        # نص رسالة الواتساب للآلي
        wa_auto = f"🎯 تحليل {u_input}%0A💰 السعر: {d['p']:.3f}%0A🚀 أهداف: {r1:.3f} - {r2:.3f}%0A🛡️ دعم: {s1:.3f}%0A🛑 وقف: {stop:.3f}"
        st.markdown(f'<a href="https://wa.me/?text={wa_auto}" target="_blank" class="wa-button">🚀 مشاركة التقرير الآلي</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 2. التقرير اليدوي ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key=f"v1_{u_input}")
with col2: m_h = st.number_input("🔝 أعلى سعر:", format="%.3f", key=f"v2_{u_input}")
with col3: m_l = st.number_input("📉 أقل سعر:", format="%.3f", key=f"v3_{u_input}")

if m_p > 0 and m_h > 0:
    piv = (m_h + m_l + m_p) / 3
    mr1, mr2 = (2 * piv) - m_l, piv + (m_h - m_l)
    ms1, ms2 = (2 * piv) - m_h, piv - (m_h - m_l)
    m_stop = ms1 * 0.98

    st.markdown(f"""
    <div class="report-card" style="border-right: 8px solid #3498db;">
        <div style="text-align:center; font-size:20px; color:#3498db;">🛠️ التقرير اليدوي لـ {u_input}</div>
        <div class="separator"></div>
        <span class="price-large">{m_p:.3f}</span>
        <div class="label-blue">🚀 أهداف: {mr1:.3f} | {mr2:.3f}</div>
        <div class="label-blue">🛡️ دعوم: {ms1:.3f} | {ms2:.3f}</div>
        <div style="color:#ff3b30; font-weight:bold;">🛑 وقف خسارة: {m_stop:.3f}</div>
    """, unsafe_allow_html=True)
    
    # نص رسالة الواتساب لليدوي (هنا حل المشكلة)
    wa_man = f"🛠️ تحليل يدوي {u_input}%0A💰 السعر: {m_p:.3f}%0A🚀 أهداف: {mr1:.3f} - {mr2:.3f}%0A🛡️ دعم: {ms1:.3f}%0A🛑 وقف: {m_stop:.3f}"
    st.markdown(f'<a href="https://wa.me/?text={wa_man}" target="_blank" class="wa-button">🚀 مشاركة التقرير اليدوي</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
