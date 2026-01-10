import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# تحسين الخطوط والألوان العامة
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .stMetric { background-color: #1e2732; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    label p { color: #ffffff !important; font-size: 18px !important; font-weight: bold !important; }
    div[data-testid="stExpander"] { background-color: #1e2732 !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "TMGH": "طلعت مصطفى", "ATQA": "مصر الوطنية للصلب"}

st.title("📊 Smart Stock Analyzer")

u_input = st.text_input("🔍 ادخل كود السهم:").upper().strip()

def build_safe_report(name, sym, p, hi, lo, cl, vol, piv, rs, ss):
    # 1. العنوان والبيانات الأساسية
    st.markdown(f"### 🎯 {name} ({sym})")
    c1, c2, c3 = st.columns(3)
    c1.metric("السعر الحالي", f"{p:.3f}")
    c2.metric("السيولة (M)", f"{vol:.1f}")
    c3.metric("التقييم", "5/6")

    # 2. الارتكاز (في تنبيه مميز)
    st.info(f"🟡 **نقطة الارتكاز المحورية:** {piv:.3f}")

    # 3. المقاومات والدعوم (أعمدة واضحة)
    col_res, col_sup = st.columns(2)
    with col_res:
        st.markdown("### 🚀 المقاومات")
        st.success(f"**م 1:** {rs[0]:.3f}")
        st.success(f"**م 2:** {rs[1]:.3f}")
        st.success(f"**م 3:** {rs[2]:.3f}")
        
    with col_sup:
        st.markdown("### 🛡️ الدعوم")
        st.error(f"**د 1:** {ss[0]:.3f}")
        st.error(f"**د 2:** {ss[1]:.3f}")
        st.error(f"**د 3:** {ss[2]:.3f}")

    # 4. شريط البيانات التاريخية
    st.code(f"🔝 أعلى: {hi:.3f} | 📉 أدنى: {lo:.3f} | 🔙 إغلاق أمس: {cl:.3f}", language="text")

    # 5. زر الواتساب (رابط بسيط ومضمون)
    wa_msg = f"🎯 تقرير: {name}\n💰 السعر: {p:.3f}\n🟡 الارتكاز: {piv:.3f}\n🚀 م1: {rs[0]:.3f}\n🛡️ د1: {ss[0]:.3f}"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
    st.markdown(f'''<a href="{wa_url}" target="_blank" style="background-color: #25D366; color: white; padding: 15px; border-radius: 10px; text-align: center; display: block; text-decoration: none; font-weight: bold;">📲 مشاركة عبر WhatsApp</a>''', unsafe_allow_html=True)

# --- محرك البحث ---
found = False
if u_input:
    try:
        ticker = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        df = yf.Ticker(ticker).history(period="5d")
        if not df.empty:
            l = df.iloc[-1]
            p, hi, lo, cl = l["Close"], l["High"], l["Low"], df["Close"].iloc[-2]
            piv = (hi + lo + p) / 3
            rs = [(2*piv)-lo, piv+(hi-lo), hi+2*(piv-lo)]
            ss = [(2*piv)-hi, piv-(hi-lo), lo-2*(hi-piv)]
            build_safe_report(ARABIC_DB.get(u_input, "سهم متداول"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, piv, rs, ss)
            found = True
    except: pass

# --- اليدوي ---
st.markdown("---")
st.subheader("🛠️ الإدخال اليدوي (لو الآلي وقف)")
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("السعر الآن", format="%.3f", key="p_75")
with c2: hm = st.number_input("أعلى سعر", format="%.3f", key="h_75")
with c3: lm = st.number_input("أقل سعر", format="%.3f", key="l_75")

with st.expander("➕ بيانات إضافية"):
    c4, c5 = st.columns(2)
    with c4: clm = st.number_input("إغلاق أمس", format="%.3f", key="c_75")
    with c5: vm = st.number_input("السيولة M", format="%.2f", key="v_75")

if pm > 0 and not found:
    piv = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*piv)-lm if lm > 0 else pm*1.02, pm*1.04, pm*1.06]
    ss = [(2*piv)-hm if hm > 0 else pm*0.98, pm*0.96, pm*0.94]
    build_safe_report(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, piv, rs, ss)
