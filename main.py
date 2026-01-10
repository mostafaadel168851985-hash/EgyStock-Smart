import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Sniper v26", layout="centered")

# --- CSS التنسيق النهائي ومنع تداخل الأكواد ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        margin: 10px auto; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .separator { border-top: 1px solid #444; margin: 12px 0; }
    .price-large { font-weight: bold; font-size: 34px; color: #4cd964; text-align: center; display: block; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 18px; }
    .info-line { margin: 8px 0; font-size: 15px; display: flex; justify-content: space-between; }
    .company-header { text-align: center; margin-bottom: 10px; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 12px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# تصحيح قاموس الأسماء العربية
ARABIC_NAMES = {
    "ATQA": "مصر الوطنية للصلب - عتاقة",
    "SWDY": "السويدي إليكتريك",
    "TMGH": "مجموعة طلعت مصطفى",
    "CRST": "كريستمارك للمقاولات",
    "MOED": "المصرية لنظم التعليم الحديث",  # تم التصحيح هنا ✅
    "FWRY": "فوري لتكنولوجيا المدفوعات",
    "COMI": "البنك التجاري الدولي",
    "EKHO": "القابضة المصرية الكويتية",
    "ABUK": "أبو قير للأسمدة",
    "MFOT": "مصر لإنتاج الأسمدة - موبكو"
}

def get_name(symbol):
    return ARABIC_NAMES.get(symbol.upper(), "شركة متداولة")

# --- واجهة البرنامج ---
st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً ATQA أو MOED):").upper()

# 1. التقرير الآلي
if u_input:
    try:
        symbol = f"{u_input}.CA"
        df = yf.Ticker(symbol).history(period="150d")
        if not df.empty:
            p = df['Close'].iloc[-1]
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            vol = (df['Volume'].iloc[-1] * p) / 1_000_000
            name_ar = get_name(u_input)
            
            # حسابات الأهداف والدعوم
            r1, r2, s1 = p*1.025, p*1.05, p*0.975
            
            st.markdown(f"""
            <div class="report-card">
                <div class="company-header">
                    <span style="color:#3498db; font-size:14px;">رمز السهم: {u_input} 💎</span><br>
                    <span style="font-size:22px; font-weight:bold;">شركة: {name_ar}</span>
                </div>
                <div class="separator"></div>
                <span class="price-large">{p:.3f}</span>
                <div class="info-line"><span>📟 RSI: <b>{rsi:.1f}</b></span> <span>💧 سيولة: <b>{vol:.1f}M</b></span></div>
                <div class="separator"></div>
                <div class="label-blue">🚀 مستويات الأهداف: <b>{r1:.3f} | {r2:.3f}</b></div>
                <div class="label-blue">🛡️ دعم رئيسي: <b>{s1:.3f}</b></div>
                <div style="color:#ff3b30; text-align:center; font-weight:bold; margin-top:10px;">🛑 وقف خسارة: {p*0.94:.3f}</div>
            """, unsafe_allow_html=True)
            
            # رسالة واتساب كاملة
            wa_text = f"🎯 تقرير {name_ar} ({u_input})%0A💰 السعر: {p:.3f}%0A🚀 أهداف: {r1:.3f} - {r2:.3f}%0A🛡️ دعم: {s1:.3f}%0A🛑 وقف: {p*0.94:.3f}%0A📊 RSI: {rsi:.1f}"
            st.markdown(f'<a href="https://wa.me/?text={wa_text}" target="_blank" class="wa-button">🚀 مشاركة التقرير الآلي</a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.error("خطأ في جلب البيانات، تأكد من الرمز.")

# 2. اللوحة اليدوية الكاملة
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة القناص اليدوية الكاملة</h3>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key="p_man")
with c2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="h_man")
with c3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f", key="l_man")

c4, c5, c6 = st.columns(3)
with c4: m_cl = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="cl_man")
with c5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="mh_man")
with c6: m_v = st.number_input("💧 سيولة (M):", format="%.2f", key="v_man")

if m_p > 0 and m_h > 0:
    name_manual = get_name(u_input if u_input else "سهم يدوي")
    piv = (m_h + m_l + m_p) / 3
    mr1, ms1 = (2 * piv) - m_l, (2 * piv) - m_h
    
    st.markdown(f"""
    <div class="report-card" style="border-right: 8px solid #3498db;">
        <div class="company-header">
            <span style="color:#3498db; font-size:14px;">تحليل يدوي لـ {u_input if u_input else '---'} 🛠️</span><br>
            <span style="font-size:22px; font-weight:bold;">شركة: {name_manual}</span>
        </div>
        <div class="separator"></div>
        <span class="price-large">{m_p:.3f}</span>
        <div class="info-line"><span>📍 الارتكاز: <b>{piv:.3f}</b></span> <span>💧 سيولة: <b>{m_v:.1f}M</b></span></div>
        <div class="separator"></div>
        <div class="info-line"><span>🚀 هدف مضاربي: <b>{mr1:.3f}</b></span> <span>🛡️ دعم: <b>{ms1:.3f}</b></span></div>
        <div class="info-line"><span>🗓️ قمة شهرية: <b>{m_mh:.3f}</b></span> <span>🎯 هدف مستثمر: <b>{m_p*1.20:.3f}</b></span></div>
        <div style="color:#ff3b30; text-align:center; font-weight:bold; margin-top:10px;">🛑 وقف الخسارة: {ms1*0.98:.3f}</div>
    """, unsafe_allow_html=True)
    
    wa_man = f"🛠️ تحليل يدوي {name_manual}%0A💰 السعر: {m_p:.3f}%0A📍 الارتكاز: {piv:.3f}%0A🚀 هدف: {mr1:.3f}%0A🛡️ دعم: {ms1:.3f}%0A🛑 وقف: {ms1*0.98:.3f}"
    st.markdown(f'<a href="https://wa.me/?text={wa_man}" target="_blank" class="wa-button">🚀 مشاركة التقرير اليدوي</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
