import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS (تفتيح الإدخال اليدوي تماماً) ---
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    /* تفتيح عناوين الإدخال اليدوي */
    label p, .stMarkdown p, h4 { color: #ffffff !important; font-weight: bold !important; opacity: 1 !important; }
    /* تفتيح خانات الإدخال */
    input { background-color: #1e2732 !important; color: #ffffff !important; border: 1px solid #3498db !important; }
    /* تفتيح الـ Expander */
    .st-emotion-cache-p4mowd { color: white !important; }
</style>
""", unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "TMGH": "طلعت مصطفى", "ATQA": "مصر الوطنية للصلب"}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 كود السهم (مثلاً ATQA):").upper().strip()

def build_svg_card(name, sym, p, hi, lo, cl, vol, piv, rs, ss, score=5):
    # رسالة الواتساب (رجعت كاملة ومنظمة)
    wa_msg = (f"🎯 تقرير: {name}\n"
              f"💰 السعر: {p:.3f}\n"
              f"🟡 الارتكاز: {piv:.3f}\n"
              f"🚀 م1: {rs[0]:.3f} | م2: {rs[1]:.3f}\n"
              f"🛡️ د1: {ss[0]:.3f} | د2: {ss[1]:.3f}\n"
              f"📊 سيولة: {vol:.1f}M")
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    # رسم الكارت بتقنية SVG (مضمونة العرض 100%)
    svg_html = f"""
    <div style="direction: rtl; text-align: right; font-family: sans-serif;">
        <svg viewBox="0 0 500 480" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="480" rx="20" fill="#1e2732" stroke="#30363d" stroke-width="2"/>
            
            <text x="250" y="40" font-size="22" font-weight="bold" fill="white" text-anchor="middle">{name} ({sym})</text>
            <line x1="50" y1="60" x2="450" y2="60" stroke="#30363d" stroke-width="1"/>
            
            <rect x="30" y="80" width="130" height="60" rx="10" fill="#0d1117"/>
            <text x="95" y="105" font-size="14" fill="#8b949e" text-anchor="middle">السعر</text>
            <text x="95" y="130" font-size="18" font-weight="bold" fill="white" text-anchor="middle">{p:.3f}</text>
            
            <rect x="185" y="80" width="130" height="60" rx="10" fill="#0d1117"/>
            <text x="250" y="105" font-size="14" fill="#8b949e" text-anchor="middle">السيولة M</text>
            <text x="250" y="130" font-size="18" font-weight="bold" fill="white" text-anchor="middle">{vol:.1f}</text>
            
            <rect x="340" y="80" width="130" height="60" rx="10" fill="#0d1117"/>
            <text x="405" y="105" font-size="14" fill="#8b949e" text-anchor="middle">التقييم</text>
            <text x="405" y="130" font-size="18" font-weight="bold" fill="#f1c40f" text-anchor="middle">{score}/6</text>

            <rect x="30" y="160" width="440" height="50" rx="10" fill="#0d1117" stroke="#f1c40f" stroke-dasharray="5"/>
            <text x="250" y="192" font-size="18" font-weight="bold" fill="#f1c40f" text-anchor="middle">🟡 الارتكاز المحوري: {piv:.3f}</text>

            <rect x="260" y="230" width="210" height="110" rx="10" fill="#161b22" stroke="#3498db"/>
            <text x="365" y="255" font-size="16" font-weight="bold" fill="#3498db" text-anchor="middle">🚀 المقاومات</text>
            <text x="365" y="285" font-size="15" fill="white" text-anchor="middle">م1: {rs[0]:.3f}</text>
            <text x="365" y="310" font-size="15" fill="white" text-anchor="middle">م2: {rs[1]:.3f}</text>
            <text x="365" y="335" font-size="15" fill="white" text-anchor="middle">م3: {rs[2]:.3f}</text>

            <rect x="30" y="230" width="210" height="110" rx="10" fill="#161b22" stroke="#f85149"/>
            <text x="135" y="255" font-size="16" font-weight="bold" fill="#f85149" text-anchor="middle">🛡️ الدعوم</text>
            <text x="135" y="285" font-size="15" fill="white" text-anchor="middle">د1: {ss[0]:.3f}</text>
            <text x="135" y="310" font-size="15" fill="white" text-anchor="middle">د2: {ss[1]:.3f}</text>
            <text x="135" y="335" font-size="15" fill="white" text-anchor="middle">د3: {ss[2]:.3f}</text>

            <rect x="30" y="360" width="440" height="40" rx="10" fill="#0d1117"/>
            <text x="250" y="385" font-size="14" fill="#8b949e" text-anchor="middle">🔝 أعلى: {hi:.3f} | 📉 أدنى: {lo:.3f} | 🔙 أمس: {cl:.3f}</text>
        </svg>
        <a href="{wa_url}" target="_blank" style="background: linear-gradient(45deg, #25D366, #128C7E); color: white; padding: 15px; border-radius: 12px; text-align: center; display: block; text-decoration: none; font-weight: bold; margin-top: 10px; font-family: sans-serif;">📲 مشاركة التقرير عبر WhatsApp</a>
    </div>
    """
    st.markdown(svg_html, unsafe_allow_html=True)

# --- جلب البيانات ---
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
            build_svg_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, piv, rs, ss)
            found = True
    except: pass

# --- الإدخال اليدوي المنير ---
st.markdown("<br><h4 style='text-align:center;'>🛠️ لوحة الإدخال اليدوي</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("السعر الآن", format="%.3f", key="p76")
with c2: hm = st.number_input("أعلى اليوم", format="%.3f", key="h76")
with c3: lm = st.number_input("أقل اليوم", format="%.3f", key="l76")

with st.expander("📊 بيانات إضافية (منورة)"):
    c4, c5 = st.columns(2)
    with c4: clm = st.number_input("إغلاق أمس", format="%.3f", key="c76")
    with c5: vm = st.number_input("السيولة (M)", format="%.2f", key="v76")

if pm > 0 and not found:
    piv = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*piv)-lm if lm > 0 else pm*1.02, pm*1.04, pm*1.06]
    ss = [(2*piv)-hm if hm > 0 else pm*0.98, pm*0.96, pm*0.94]
    build_svg_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, piv, rs, ss, score=3)
