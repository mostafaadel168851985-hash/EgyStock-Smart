import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper v23", layout="centered")

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
    .price-large { font-weight: bold; font-size: 32px; color: #4cd964; text-align: center; display: block; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 18px; }
    .info-line { margin: 8px 0; font-size: 16px; display: flex; justify-content: space-between; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 12px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# قاموس الأسماء العربية
ARABIC_NAMES = {
    "ATQA": "مصر الوطنية للصلب - عتاقة",
    "SWDY": "السويدي إليكتريك",
    "TMGH": "مجموعة طلعت مصطفى",
    "CRST": "كريستمارك للمقاولات",
    "MOED": "مصر لأسمنت قنا",
    "FWRY": "فوري لتكنولوجيا المدفوعات",
    "COMI": "البنك التجاري الدولي",
    "EKHO": "القابضة المصرية الكويتية",
    "ABUK": "أبو قير للأسمدة",
    "MFOT": "مصر لإنتاج الأسمدة - موبكو",
    "ORAS": "أوراسكوم للإنشاء",
    "BTEL": "البانر لتكنولوجيا الاتصالات",
    "UNIT": "يونايتد للاستثمار"
}

def get_company_name(symbol):
    return ARABIC_NAMES.get(symbol.upper(), symbol)

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

# --- 1. التقرير الآلي (البيانات الكاملة) ---
if u_input:
    d = get_auto_data(u_input)
    name_ar = get_company_name(u_input)
    if d:
        r1, r2 = d['p']*1.025, d['p']*1.05
        s1, s2 = d['p']*0.975, d['p']*0.95
        
        st.markdown(f"""
        <div class="report-card">
            <div style="text-align:center; font-size:22px; font-weight:bold;">💎 {name_ar}</div>
            <div class="separator"></div>
            <span class="price-large">{d['p']:.3f}</span>
            <div class="info-line"><span>📟 مؤشر RSI: <b>{d['rsi']:.1f}</b></span> <span>💧 سيولة الجلسة: <b>{d['vol']:.1f}M</b></span></div>
            <div class="separator"></div>
            <div class="label-blue">🔍 اتجاهات السهم:</div>
            <div class="info-line"><span>قصير: {d['t_s']}</span> <span>متوسط: {d['t_m']}</span></div>
            <div class="info-line"><span>طويل المدى: {d['t_l']}</span></div>
            <div class="separator"></div>
            <div class="label-blue">🚀 مستويات الأهداف:</div>
            <div class="info-line"><span>🎯 هدف 1: <b>{r1:.3f}</b></span> <span>🎯 هدف 2: <b>{r2:.3f}</b></span></div>
            <div class="separator"></div>
            <div class="label-blue">🛡️ مستويات الدعم:</div>
            <div class="info-line"><span>🔸 دعم 1: <b>{s1:.3f}</b></span> <span>🔸 دعم 2: <b>{s2:.3f}</b></span></div>
            <div style="color:#ff3b30; text-align:center; font-weight:bold; margin-top:10px;">🛑 وقف خسارة: {d['p']*0.94:.3f}</div>
        """, unsafe_allow_html=True)
        
        wa_msg = f"🎯 تحليل {name_ar}%0A💰 السعر: {d['p']:.3f}%0A🚀 أهداف: {r1:.3f} - {r2:.3f}%0A🛡️ دعم: {s1:.3f}%0A🛑 وقف: {d['p']*0.94:.3f}"
        st.markdown(f'<a href="https://wa.me/?text={wa_msg}" target="_blank" class="wa-button">🚀 مشاركة التقرير الآلي</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 2. الإدخال اليدوي (بيانات الصور الكاملة) ---
st.markdown("<hr style='border-color:#333;'>")
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة القناص اليدوية</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key=f"p_{u_input}")
with col2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f", key=f"h_{u_input}")
with col3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f", key=f"l_{u_input}")

col4, col5, col6 = st.columns(3)
with col4: m_cl = st.number_input("↩️ إغلاق أمس:", format="%.3f", key=f"c_{u_input}")
with col5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key=f"mh_{u_input}")
with col6: m_v = st.number_input("💧 سيولة (M):", format="%.2f", key=f"v_{u_input}")

if m_p > 0 and m_h > 0:
    name_ar = get_company_name(u_input if u_input else "سهم يدوي")
    piv = (m_h + m_l + m_p) / 3
    r1, r2 = (2 * piv) - m_l, piv + (m_h - m_l)
    s1, s2 = (2 * piv) - m_h, piv - (m_h - m_l)
    trend = "صاعد 🟢" if m_p > m_cl else "هابط 🔴"
    
    st.markdown(f"""
    <div class="report-card" style="border-right: 8px solid #3498db;">
        <div style="text-align:center; font-size:22px; font-weight:bold; color:#3498db;">🛠️ تقرير {name_ar} (يدوي)</div>
        <div class="separator"></div>
        <span class="price-large">{m_p:.3f}</span>
        <div class="info-line"><span>📍 نقطة الارتكاز: <b>{piv:.3f}</b></span> <span>💧 السيولة: <b>{m_v:.1f}M</b></span></div>
        <div class="separator"></div>
        <div class="label-blue">🔍 تحليل الحالة:</div>
        <div class="info-line">📈 الاتجاه الحالي: {trend}</div>
        <div class="info-line">🏢 هدف المستثمر: <b>{m_p*1.20:.3f}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🚀 مستويات المقاومة:</div>
        <div class="info-line"><span>🔹 هدف 1: <b>{r1:.3f}</b></span> <span>🔹 هدف 2: <b>{r2:.3f}</b></span></div>
        <div class="separator"></div>
        <div class="label-blue">🛡️ مستويات الدعم:</div>
        <div class="info-line"><span>🔸 دعم 1: <b>{s1:.3f}</b></span> <span>🔸 دعم 2: <b>{s2:.3f}</b></span></div>
        <div style="color:#ff3b30; text-align:center; font-weight:bold; margin-top:10px;">🛑 وقف خسارة: {s1*0.98:.3f}</div>
        <a href="https://wa.me/?text=تحليل يدوي لـ {name_ar}: {m_p:.3f}" class="wa-button">🚀 مشاركة التقرير اليدوي</a>
    </div>
    """, unsafe_allow_html=True)
