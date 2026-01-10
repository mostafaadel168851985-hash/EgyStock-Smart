import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS (تفتيح الخطوط وإلغاء البهتان) ---
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    /* تفتيح خانات الإدخال والـ Expander */
    .stMarkdown p, label p, .st-emotion-cache-p4mowd { 
        color: #ffffff !important; 
        font-weight: bold !important; 
        font-size: 16px !important;
        opacity: 1 !important;
    }
    input { background-color: #1e2732 !important; color: white !important; }
    /* تنسيق الكارت يدوياً عبر بلوكات Streamlit */
    div[data-testid="stVerticalBlock"] > div { border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "TMGH": "طلعت مصطفى", "ATQA": "مصر الوطنية للصلب"}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل كود السهم (مثلاً TMGH):").upper().strip()

def build_native_card(name, sym, p, hi, lo, cl, vol, piv, rs, ss, score=5):
    # رسالة الواتساب الكاملة
    wa_msg = (f"🎯 تقرير: {name}\n💰 السعر: {p:.3f}\n🟡 الارتكاز: {piv:.3f}\n"
              f"🚀 م1: {rs[0]:.3f} | م2: {rs[1]:.3f}\n🛡️ د1: {ss[0]:.3f} | د2: {ss[1]:.3f}\n"
              f"📊 سيولة: {vol:.1f}M")
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    # بناء الكارت باستخدام حاوية Streamlit الرسمية
    with st.container(border=True):
        st.markdown(f"<h2 style='text-align:center; color:white;'>{name} ({sym})</h2>", unsafe_allow_html=True)
        
        # الصف الأول: السعر، التقييم، السيولة
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 السعر", f"{p:.3f}")
        c2.metric("⭐ التقييم", f"{score}/6")
        c3.metric("📊 السيولة M", f"{vol:.1f}")

        # بوكس الارتكاز
        st.help(f"🟡 نقطة الارتكاز المحورية: {piv:.3f}")

        # الدعوم والمقاومات
        col_r, col_s = st.columns(2)
        with col_r:
            st.info(f"🚀 **المقاومات**\n\nم1: {rs[0]:.3f}\n\nم2: {rs[1]:.3f}\n\nم3: {rs[2]:.3f}")
        with col_s:
            st.error(f"🛡️ **الدعوم**\n\nد1: {ss[0]:.3f}\n\nد2: {ss[1]:.3f}\n\nد3: {ss[2]:.3f}")

        # بيانات تاريخية
        st.warning(f"🔝 أعلى: {hi:.3f}  |  📉 أدنى: {lo:.3f}  |  🔙 أمس: {cl:.3f}")
        
        # زر الواتساب
        st.markdown(f'''<a href="{wa_url}" target="_blank" style="background-color: #25D366; color: white; padding: 12px; border-radius: 10px; text-align: center; display: block; text-decoration: none; font-weight: bold; margin-top: 10px;">📲 مشاركة التقرير عبر WhatsApp</a>''', unsafe_allow_html=True)

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
            build_native_card(ARABIC_DB.get(u_input, "سهم متداول"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, piv, rs, ss)
            found = True
    except: pass

# --- الإدخال اليدوي (حل مشكلة الفونت المطفي) ---
st.markdown("<br><h4 style='text-align:center; color:white;'>🛠️ لوحة الإدخال اليدوي</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("💵 السعر الآن", format="%.3f", key="p77")
with c2: hm = st.number_input("🔝 أعلى اليوم", format="%.3f", key="h77")
with c3: lm = st.number_input("📉 أقل اليوم", format="%.3f", key="l77")

with st.expander("📊 بيانات إضافية (اضغط هنا للفتح)"):
    st.markdown("<p style='color:white;'>ادخل البيانات التالية بدقة:</p>", unsafe_allow_html=True)
    cx, cy = st.columns(2)
    with cx: clm = st.number_input("↩️ إغلاق أمس", format="%.3f", key="c77")
    with cy: vm = st.number_input("💧 السيولة M", format="%.2f", key="v77")

if pm > 0 and not found:
    piv = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*piv)-lm if lm > 0 else pm*1.02, pm*1.04, pm*1.06]
    ss = [(2*piv)-hm if hm > 0 else pm*0.98, pm*0.96, pm*0.94]
    build_native_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, piv, rs, ss, score=3)
