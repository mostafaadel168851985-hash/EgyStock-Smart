import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

# إعدادات الصفحة
st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS لتفتيح الخطوط 100% ---
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    /* تفتيح الخطوط في كل مكان */
    .stMarkdown, p, label, .st-at, .st-ae { 
        color: #ffffff !important; 
        font-weight: bold !important; 
        opacity: 1 !important; 
    }
    /* تحسين شكل المدخلات */
    .stNumberInput input { background-color: #1e2732 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# قاعدة البيانات المحدثة
ARABIC_DB = {
    "SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم",
    "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "TMGH": "مجموعة طلعت مصطفى",
    "SWDY": "السويدي إليكتريك", "ATQA": "مصر الوطنية للصلب", "UNIT": "المتحدة للإسكان",
    "FWRY": "فوري للمدفوعات", "BTFH": "بلتون المالية"
}

st.title("📈 Smart Stock Analyzer")

# إدخال الكود
u_input = st.text_input("🔍 ادخل رمز السهم (مثلاً TMGH):").upper().strip()

def show_modern_report(name, sym, p, hi, lo, cl, vol, piv, rs, ss):
    # 1. العنوان (اسم الشركة + الرمز)
    st.subheader(f"📊 {name} | {sym}")
    
    # 2. كروت البيانات الأساسية
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 السعر الآن", f"{p:.3f}")
        c2.metric("⭐ التقييم", "5/6")
        c3.metric("💧 السيولة M", f"{vol:.1f}")

        # 3. الارتكاز والدعوم والمقاومات (نظام الجداول لضمان الوضوح)
        st.write(f"### 🟡 نقطة الارتكاز: `{piv:.3f}`")
        
        col_r, col_s = st.columns(2)
        with col_r:
            st.success(f"**🚀 المقاومات**\n\n م1: {rs[0]:.3f}\n\n م2: {rs[1]:.3f}\n\n م3: {rs[2]:.3f}")
        with col_s:
            st.error(f"**🛡️ الدعوم**\n\n د1: {ss[0]:.3f}\n\n د2: {ss[1]:.3f}\n\n د3: {ss[2]:.3f}")

        st.info(f"🔝 أعلى: {hi:.3f} | 📉 أدنى: {lo:.3f} | 🔙 أمس: {cl:.3f}")

    # 4. رابط الواتساب المطور (Modern & Smart)
    wa_msg = (f"🎯 تقرير سهم: {name} ({sym})\n"
              f"💰 السعر: {p:.3f}\n"
              f"🟡 الارتكاز: {piv:.3f}\n"
              f"🚀 م1: {rs[0]:.3f}\n"
              f"🛡️ د1: {ss[0]:.3f}\n"
              f"📊 سيولة: {vol:.1f}M")
    
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
    
    # زرار مودرن باستخدام ستايل Streamlit الأصلي
    st.link_button("📲 مشاركة التقرير الذكي عبر WhatsApp", wa_url, use_container_width=True)

# --- محرك البحث ---
found_auto = False
if u_input:
    try:
        ticker = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        data = yf.Ticker(ticker).history(period="5d")
        if not data.empty:
            curr = data.iloc[-1]
            p, hi, lo, cl = curr["Close"], curr["High"], curr["Low"], data["Close"].iloc[-2]
            piv = (hi + lo + p) / 3
            rs = [(2*piv)-lo, piv+(hi-lo), hi+2*(piv-lo)]
            ss = [(2*piv)-hi, piv-(hi-lo), lo-2*(hi-piv)]
            
            show_modern_report(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (curr['Volume']*p)/1e6, piv, rs, ss)
            found_auto = True
    except:
        st.error("⚠️ عذراً، تعذر جلب البيانات تلقائياً. يرجى استخدام الإدخال اليدوي.")

# --- الإدخال اليدوي (بخطوط ناصعة 100%) ---
st.write("---")
st.write("### 🛠️ لوحة الإدخال اليدوي (فونت ناصع)")

col1, col2, col3 = st.columns(3)
with col1: pm = st.number_input("💵 السعر الآن", format="%.3f", key="pm8")
with col2: hm = st.number_input("🔝 أعلى سعر", format="%.3f", key="hm8")
with col3: lm = st.number_input("📉 أقل سعر", format="%.3f", key="lm8")

with st.expander("📊 بيانات إضافية (مؤمنة من البهتان)"):
    st.write("⚠️ ادخل بيانات أمس والسيولة لتكتمل الرسالة:")
    cx, cy = st.columns(2)
    with cx: clm = st.number_input("🔙 إغلاق أمس", format="%.3f", key="clm8")
    with cy: vm = st.number_input("💧 السيولة M", format="%.2f", key="vm8")

if pm > 0 and not found_auto:
    piv_m = (hm + lm + pm) / 3 if hm > 0 else pm
    rs_m = [(2*piv_m)-lm if lm > 0 else pm*1.02, pm*1.04, pm*1.06]
    ss_m = [(2*piv_m)-hm if hm > 0 else pm*0.98, pm*0.96, pm*0.94]
    
    show_modern_report(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, piv_m, rs_m, ss_m)
