import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Sniper v27", layout="centered")

# --- CSS التنسيق الاحترافي المستوحى من صورك ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        margin: 10px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .separator { border-top: 1px solid #444; margin: 12px 0; }
    .price-large { font-weight: bold; font-size: 36px; color: #4cd964; text-align: center; display: block; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 17px; margin-bottom: 5px; }
    .info-line { margin: 8px 0; font-size: 15px; display: flex; justify-content: space-between; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 12px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

ARABIC_NAMES = {
    "ATQA": "مصر الوطنية للصلب - عتاقة",
    "SWDY": "السويدي إليكتريك",
    "TMGH": "مجموعة طلعت مصطفى",
    "CRST": "كريستمارك للمقاولات",
    "MOED": "المصرية لنظم التعليم الحديث",
    "FWRY": "فوري لتكنولوجيا المدفوعات",
    "COMI": "البنك التجاري الدولي"
}

def get_name(symbol):
    return ARABIC_NAMES.get(symbol.upper(), "شركة مقيدة")

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً ATQA أو MOED):").upper()

# --- 1. كارت التحليل الآلي الشامل (نسخة التليجرام المحدثة) ---
if u_input:
    try:
        symbol = f"{u_input}.CA"
        df = yf.Ticker(symbol).history(period="150d")
        if not df.empty:
            p = df['Close'].iloc[-1]
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            vol = (df['Volume'].iloc[-1] * p) / 1_000_000
            name_ar = get_name(u_input)
            
            # الحسابات الفنية
            r1, r2 = p*1.025, p*1.05
            s1, s2 = p*0.975, p*0.95
            inv_target = p * 1.20 # هدف مستثمر
            
            st.markdown(f"""
            <div class="report-card">
                <div style="text-align:center;">
                    <span style="color:#3498db; font-size:14px;">💎 الرمز: {u_input}</span><br>
                    <span style="font-size:22px; font-weight:bold;">شركة: {name_ar}</span>
                </div>
                <div class="separator"></div>
                <span class="price-large">{p:.3f}</span>
                <div class="info-line"><span>📟 مؤشر RSI: <b>{rsi:.1f}</b></span> <span>💧 السيولة: <b>{vol:.1f}M</b></span></div>
                <div class="separator"></div>
                <div class="label-blue">🏹 قسم المضارب اللحظي:</div>
                <div class="info-line"><span>🚀 هدف مضاربي: <b>{r1:.3f}</b></span> <span>🛡️ دعم أول: <b>{s1:.3f}</b></span></div>
                <div class="info-line"><span>🚀 هدف ثانٍ: <b>{r2:.3f}</b></span> <span>🛡️ دعم ثانٍ: <b>{s2:.3f}</b></span></div>
                <div class="separator"></div>
                <div class="label-blue">🏢 قسم المستثمر:</div>
                <div class="info-line"><span>🎯 هدف المستهدف (+20%): <b>{inv_target:.3f}</b></span></div>
                <div style="color:#ff3b30; text-align:center; font-weight:bold; margin-top:10px;">🛑 وقف خسارة: {p*0.94:.3f}</div>
            """, unsafe_allow_html=True)
            
            wa_text = f"🎯 تقرير {name_ar} (%0A💰 السعر: {p:.3f}%0A🚀 أهداف: {r1:.3f} - {r2:.3f}%0A🛡️ دعوم: {s1:.3f} - {s2:.3f}%0A🎯 هدف مستثمر: {inv_target:.3f}%0A🛑 وقف: {p*0.94:.3f}"
            st.markdown(f'<a href="https://wa.me/?text={wa_text}" target="_blank" class="wa-button">🚀 مشاركة التقرير الشامل</a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except: st.error("تأكد من الرمز الصحيح")

# --- 2. لوحة الإدخال اليدوي الكاملة ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة القناص اليدوية</h3>", unsafe_allow_html=True)

# ... (خانات الإدخال اليدوي الستة كما هي في الكود السابق لضمان الدقة) ...
c1, c2, c3 = st.columns(3)
with c1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key="p_m")
with c2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="h_m")
with c3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f", key="l_m")
c4, c5, c6 = st.columns(3)
with c4: m_cl = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="cl_m")
with c5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="mh_m")
with c6: m_v = st.number_input("💧 سيولة (M):", format="%.2f", key="v_m")

if m_p > 0 and m_h > 0:
    name_man = get_name(u_input if u_input else "سهم يدوي")
    piv = (m_h + m_l + m_p) / 3
    mr1, ms1 = (2 * piv) - m_l, (2 * piv) - m_h
    
    st.markdown(f"""
    <div class="report-card" style="border-right: 8px solid #3498db;">
        <div style="text-align:center;">
            <span style="color:#3498db;">تحليل يدوي 🛠️</span><br>
            <span style="font-size:20px; font-weight:bold;">{name_man}</span>
        </div>
        <div class="separator"></div>
        <span class="price-large">{m_p:.3f}</span>
        <div class="info-line"><span>📍 الارتكاز: <b>{piv:.3f}</b></span> <span>💧 سيولة: <b>{m_v:.1f}M</b></span></div>
        <div class="info-line"><span>🚀 هدف مضاربي: <b>{mr1:.3f}</b></span> <span>🛡️ دعم: <b>{ms1:.3f}</b></span></div>
        <div class="info-line"><span>🗓️ قمة شهرية: <b>{m_mh:.3f}</b></span> <span>🎯 هدف مستثمر: <b>{m_p*1.20:.3f}</b></span></div>
        <div style="color:#ff3b30; text-align:center; font-weight:bold; margin-top:5px;">🛑 وقف الخسارة: {ms1*0.98:.3f}</div>
        <a href="https://wa.me/?text=تحليل يدوي {name_man}: {m_p:.3f}" class="wa-button">🚀 مشاركة اليدوي</a>
    </div>
    """, unsafe_allow_html=True)
