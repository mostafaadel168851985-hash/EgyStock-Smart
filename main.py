import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper v24", layout="centered")

# --- CSS التنسيق الاحترافي الموحد ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        max-width: 450px; margin: 15px auto;
    }
    .separator { border-top: 1px solid #444; margin: 12px 0; }
    .price-large { font-weight: bold; font-size: 32px; color: #4cd964; text-align: center; display: block; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 18px; }
    .info-line { margin: 8px 0; font-size: 16px; display: flex; justify-content: space-between; }
    .company-info { text-align: center; margin-bottom: 10px; }
    .company-symbol { color: #8b949e; font-size: 16px; font-weight: bold; }
    .company-name { color: #ffffff; font-size: 22px; font-weight: bold; display: block; margin-top: 5px; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 12px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# قاموس الأسماء العربية (القائمة اللي بتظهر في صورك)
ARABIC_NAMES = {
    "ATQA": "مصر الوطنية للصلب - عتاقة",
    "SWDY": "السويدي إليكتريك",
    "TMGH": "مجموعة طلعت مصطفى",
    "CRST": "كريستمارك للمقاولات",
    "MOED": "مصر لأسمنت قنا",
    "FWRY": "فوري لتكنولوجيا المدفوعات",
    "COMI": "البنك التجاري الدولي"
}

def get_company_name(symbol):
    return ARABIC_NAMES.get(symbol.upper(), "شركة غير مسجلة")

def get_auto_data(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        df = yf.Ticker(symbol).history(period="150d")
        if df.empty: return None
        p = df['Close'].iloc[-1]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        vol = (df['Volume'].iloc[-1] * p) / 1_000_000
        ma20, ma50, ma100 = df['Close'].rolling(20).mean().iloc[-1], df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(100).mean().iloc[-1]
        return {"p": p, "rsi": rsi, "vol": vol, 
                "t_s": "صاعد 🟢" if p > ma20 else "هابط 🔴",
                "t_m": "صاعد 🟢" if p > ma50 else "هابط 🔴",
                "t_l": "صاعد 🟢" if p > ma100 else "هابط 🔴"}
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً ATQA):").upper()

# --- 1. التقرير الآلي ---
if u_input:
    d = get_auto_data(u_input)
    name_ar = get_company_name(u_input)
    if d:
        st.markdown(f"""
        <div class="report-card">
            <div class="company-info">
                <span class="company-symbol">رمز السهم: {u_input} 💎</span>
                <span class="company-name">شركة: {name_ar}</span>
            </div>
            <div class="separator"></div>
            <span class="price-large">{d['p']:.3f}</span>
            <div class="info-line"><span>📟 RSI: <b>{d['rsi']:.1f}</b></span> <span>💧 سيولة: <b>{d['vol']:.1f}M</b></span></div>
            <div class="separator"></div>
            <div class="label-blue">🔍 الاتجاهات:</div>
            <div class="info-line"><span>قصير: {d['t_s']}</span> <span>متوسط: {d['t_m']}</span></div>
            <div class="info-line"><span>طويل: {d['t_l']}</span></div>
            <div class="separator"></div>
            <div class="label-blue">🚀 الأهداف: <b>{d['p']*1.025:.3f} | {d['p']*1.05:.3f}</b></div>
            <div class="label-blue">🛡️ الدعوم: <b>{d['p']*0.975:.3f} | {d['p']*0.95:.3f}</b></div>
            <div style="color:#ff3b30; text-align:center; font-weight:bold; margin-top:10px;">🛑 وقف خسارة: {d['p']*0.94:.3f}</div>
        """, unsafe_allow_html=True)
        
        wa_msg = f"🎯 تحليل {name_ar} ({u_input})%0A💰 السعر: {d['p']:.3f}%0A🚀 أهداف: {d['p']*1.025:.3f}-{d['p']*1.05:.3f}%0A🛑 وقف: {d['p']*0.94:.3f}"
        st.markdown(f'<a href="https://wa.me/?text={wa_msg}" target="_blank" class="wa-button">🚀 مشاركة التقرير</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 2. الإدخال اليدوي (بنفس التنسيق) ---
st.markdown("<hr style='border-color:#333;'>")
c1, c2, c3 = st.columns(3)
with c1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key=f"p_{u_input}")
with c2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f", key=f"h_{u_input}")
with c3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f", key=f"l_{u_input}")

if m_p > 0 and m_h > 0:
    name_ar = get_company_name(u_input if u_input else "سهم يدوي")
    piv = (m_h + m_l + m_p) / 3
    st.markdown(f"""
    <div class="report-card" style="border-right: 8px solid #3498db;">
        <div class="company-info">
            <span class="company-symbol" style="color:#3498db;">رمز السهم: {u_input if u_input else '---'} 🛠️</span>
            <span class="company-name">شركة: {name_ar}</span>
        </div>
        <div class="separator"></div>
        <span class="price-large">{m_p:.3f}</span>
        <div style="text-align:center; color:#3498db; font-weight:bold;">📍 نقطة الارتكاز: {piv:.3f}</div>
        <div class="separator"></div>
        <div class="label-blue">🏢 هدف المستثمر: <b>{m_p*1.20:.3f}</b></div>
    </div>
    """, unsafe_allow_html=True)
