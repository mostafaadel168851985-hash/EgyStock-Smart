import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- تحسين المظهر العام ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .stNumberInput, .stTextInput {background-color: #1e2732 !important; color: white !important;}
    </style>
    """, unsafe_allow_html=True)

# قاعدة بيانات الأسماء
ARABIC_DB = {
    "SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم",
    "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري للمدفوعات",
    "BTFH": "بلتون المالية", "TMGH": "طلعت مصطفى", "SWDY": "السويدي إليكتريك",
    "ATQA": "مصر الوطنية للصلب", "UNIT": "المتحدة للإسكان", "AMOC": "إسكندرية للزيوت"
}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)

u_input = st.text_input("🔍 ادخل كود السهم (مثلاً ABUK):").upper().strip()

def build_card_v70(name, sym, p, high, low, close_prev, vol, score, pivot, rs, ss):
    wa_msg = f"📊 تقرير {name}\n💰 السعر: {p:.2f}\n⭐ التقييم: {score}/6"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    # الكارت الخارجي
    with st.container():
        st.markdown(f"""
        <div style="background-color: #1e2732; padding: 20px; border-radius: 15px; border: 1px solid #30363d; direction: rtl; text-align: right;">
            <h2 style="text-align:center; color:white; margin-bottom:5px;">{name} ({sym})</h2>
            <hr style="border-color:#444;">
        </div>
        """, unsafe_allow_html=True)

        # صف البيانات الأساسية (باستخدام أعمدة Streamlit الأصلية)
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 السعر الآن", f"{p:.3f}")
        c2.metric("⭐ التقييم", f"{score}/6")
        c3.metric("📊 السيولة M", f"{vol:.1f}")

        # صندوق المؤشرات والارتكاز
        st.markdown(f"""
        <div style="background:#0d1117; padding:15px; border-radius:10px; border:1px dashed #3498db; margin:10px 0; text-align:center;">
            <p style="color:#3498db; font-weight:bold; margin-bottom:10px;">🔍 الفحص الفني والارتكاز</p>
            <p style="color:white; font-size:18px;">🟡 نقطة الارتكاز: <b style="color:#f1c40f;">{pivot:.3f}</b></p>
        </div>
        """, unsafe_allow_html=True)

        # الدعوم والمقاومات
        col_r, col_s = st.columns(2)
        with col_r:
            st.markdown(f"""
            <div style="background:#21262d; padding:10px; border-radius:8px; border-right:4px solid #3498db;">
                <p style="color:#3498db; font-weight:bold;">🚀 المقاومات</p>
                <p style="color:white;">م 1: {rs[0]:.3f}<br>م 2: {rs[1]:.3f}<br>م 3: {rs[2]:.3f}</p>
            </div>""", unsafe_allow_html=True)
        with col_s:
            st.markdown(f"""
            <div style="background:#21262d; padding:10px; border-radius:8px; border-right:4px solid #e74c3c;">
                <p style="color:#e74c3c; font-weight:bold;">🛡️ الدعوم</p>
                <p style="color:white;">د 1: {ss[0]:.3f}<br>د 2: {ss[1]:.3f}<br>د 3: {ss[2]:.3f}</p>
            </div>""", unsafe_allow_html=True)

        # البيانات التاريخية
        st.markdown(f"""
        <div style="background:#0d1117; padding:10px; border-radius:8px; margin-top:10px; display:flex; justify-content:space-between; font-size:12px; color:#aaa;">
            <span>🔝 أعلى: {high:.3f}</span> | <span>📉 أدنى: {low:.3f}</span> | <span>🔙 أمس: {close_prev:.3f}</span>
        </div>
        <a href="{wa_url}" target="_blank" style="background: linear-gradient(45deg, #25d366, #128c7e); color: white; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; display: block; text-decoration: none; margin-top: 15px;">📲 مشاركة عبر WhatsApp</a>
        """, unsafe_allow_html=True)

# --- التشغيل ---
has_data = False
if u_input:
    try:
        ticker = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        df = yf.Ticker(ticker).history(period="5d")
        if not df.empty:
            l = df.iloc[-1]
            p, hi, lo, cl = l["Close"], l["High"], l["Low"], df["Close"].iloc[-2]
            pivot = (hi + lo + p) / 3
            rs = [(2*pivot)-lo, pivot+(hi-lo), hi+2*(pivot-lo)]
            ss = [(2*pivot)-hi, pivot-(hi-lo), lo-2*(hi-pivot)]
            build_card_v70(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, 4, pivot, rs, ss)
            has_data = True
    except: pass

# --- اليدوي ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("💵 السعر الآن:", format="%.3f", key="p_v70")
with c2: hm = st.number_input("🔝 أعلى سعر:", format="%.3f", key="h_v70")
with c3: lm = st.number_input("📉 أقل سعر:", format="%.3f", key="l_v70")

with st.expander("📊 بيانات إضافية"):
    c4, c5 = st.columns(2)
    with c4: clm = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="cl_v70")
    with c5: vm = st.number_input("💧 السيولة (M):", format="%.2f", key="v_v70")

if pm > 0 and not has_data:
    pivot = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*pivot)-lm if lm>0 else pm*1.02, pm*1.04, pm*1.06]
    ss = [(2*pivot)-hm if hm>0 else pm*0.98, pm*0.96, pm*0.94]
    build_card_v70(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, 3, pivot, rs, ss)
