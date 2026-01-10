import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="Smart Stock Analyzer Pro", layout="centered")

# --- CSS التنسيق النهائي ---
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    label p, .stMarkdown p, .stExpander p { color: #ffffff !important; font-weight: bold !important; opacity: 1 !important; }
    input { background-color: #1e2732 !important; color: white !important; border: 1px solid #3498db !important; }

    /* زرار الواتساب المدمج */
    .stButton>button {
        background: linear-gradient(90deg, #25D366, #128C7E) !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border-radius: 0px 0px 15px 15px !important;
        border: none !important;
        padding: 14px !important;
        width: 100% !important;
        margin-top: -25px !important;
        box-shadow: 0 4px 15px rgba(37,211,102,0.3) !important;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "TMGH": "طلعت مصطفى", "ATQA": "مصر الوطنية للصلب", "SWDY": "السويدي إليكتريك", "FWRY": "فوري", "BTFH": "بلتون"}

st.title("🚀 Smart Stock Analyzer Pro")
u_input = st.text_input("🔍 ادخل رمز السهم:").upper().strip()

def build_pro_card(name, sym, p, hi, lo, cl, vol, piv, rs, ss):
    # حساب قوة الاتجاه والنسبة
    diff = ((p - piv) / piv) * 100
    strength = min(abs(diff) * 10, 100) # معادلة تقريبية لقوة الزخم
    trend_icon = "📈" if p > piv else "📉"
    recommendation = "دخول قوي" if p > rs[0] else "شراء" if p > piv else "انتظار"
    
    card_html = f"""
    <div style="direction: rtl; font-family: sans-serif; background: #1e2732; border-radius: 15px 15px 0px 0px; border: 1px solid #30363d; padding: 25px; color: white;">
        <div style="text-align: center; margin-bottom: 15px;">
            <h1 style="margin: 0; font-size: 24px;">{name}</h1>
            <code style="color: #3498db; font-size: 16px;">{sym}</code>
        </div>
        
        <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
            <div style="text-align: center; background: #0d1117; padding: 10px; border-radius: 12px; flex: 1; margin: 0 5px; border: 1px solid #3d444d;">
                <div style="color: #8b949e; font-size: 12px;">قوة الاتجاه</div>
                <div style="font-size: 18px; font-weight: bold; color: #f1c40f;">{strength:.1f}% {trend_icon}</div>
            </div>
            <div style="text-align: center; background: #0d1117; padding: 10px; border-radius: 12px; flex: 1; margin: 0 5px; border: 1px solid #3d444d;">
                <div style="color: #8b949e; font-size: 12px;">نبض السيولة</div>
                <div style="font-size: 18px; font-weight: bold; color: #2ecc71;">{vol:.1f}M 🔥</div>
            </div>
        </div>

        <div style="background: #0d1117; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #f1c40f; margin-bottom: 20px;">
            <div style="color: #f1c40f; font-size: 14px; font-weight: bold;">🟡 نقطة الارتكاز المحورية</div>
            <div style="font-size: 28px; font-weight: bold; color: white; margin-top: 5px;">{piv:.3f}</div>
            <div style="color: #3498db; font-size: 14px; margin-top: 5px;">التوصية: <b>{recommendation}</b></div>
        </div>

        <div style="display: flex; justify-content: space-between; gap: 15px;">
            <div style="flex: 1; background: #161b22; padding: 15px; border-radius: 12px; border-right: 5px solid #3498db;">
                <div style="color: #3498db; font-weight: bold; margin-bottom: 10px;">🚀 المقاومات</div>
                <div style="line-height: 1.8;">م1: {rs[0]:.3f}<br>م2: {rs[1]:.3f}<br>م3: {rs[2]:.3f}</div>
            </div>
            <div style="flex: 1; background: #161b22; padding: 15px; border-radius: 12px; border-right: 5px solid #e74c3c;">
                <div style="color: #e74c3c; font-weight: bold; margin-bottom: 10px;">🛡️ الدعوم</div>
                <div style="line-height: 1.8;">د1: {ss[0]:.3f}<br>د2: {ss[1]:.3f}<br>د3: {ss[2]:.3f}</div>
            </div>
        </div>

        <div style="background: #0d1117; padding: 12px; border-radius: 10px; margin-top: 20px; border: 1px solid #30363d; font-size: 13px; text-align: center; color: #8b949e;">
            السعر: <b style="color:white">{p:.3f}</b> | أعلى: {hi:.3f} | أدنى: {lo:.3f} | أمس: {cl:.3f}
        </div>
    </div>
    """
    components.html(card_html, height=580)

    # رسالة الواتساب المحدثة
    wa_msg = (f"🎯 تقرير: {name} ({sym})\n💰 السعر: {p:.3f}\n🟡 الارتكاز: {piv:.3f}\n"
              f"📊 قوة الاتجاه: {strength:.1f}% {trend_icon}\n🔥 السيولة: {vol:.1f}M\n"
              f"🚀 م1: {rs[0]:.3f} | 🛡️ د1: {ss[0]:.3f}")
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
    st.link_button("📲 مشاركة التقرير الاحترافي عبر WhatsApp", wa_url)

# --- المحرك ---
found = False
if u_input:
    try:
        ticker = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        df = yf.Ticker(ticker).history(period="5d")
        if not df.empty:
            l = df.iloc[-1]
            p, hi, lo, cl = l["Close"], l["High"], l["Low"], df["Close"].iloc[-2]
            piv = (hi + lo + p) / 3
            rs, ss = [(2*piv)-lo, piv+(hi-lo), hi+2*(piv-lo)], [(2*piv)-hi, piv-(hi-lo), lo-2*(hi-piv)]
            build_pro_card(ARABIC_DB.get(u_input, "سهم متداول"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, piv, rs, ss)
            found = True
    except: pass

# --- اليدوي ---
if not found:
    st.markdown("---")
    st.subheader("🛠️ الإدخال اليدوي")
    c1, c2, c3 = st.columns(3)
    with c1: pm = st.number_input("💵 السعر الآن", format="%.3f", key="p83")
    with c2: hm = st.number_input("🔝 أعلى سعر", format="%.3f", key="h83")
    with c3: lm = st.number_input("📉 أقل سعر", format="%.3f", key="l83")
    with st.expander("📊 بيانات إضافية"):
        cx, cy = st.columns(2)
        with cx: clm = st.number_input("↩️ إغلاق أمس", format="%.3f", key="c83")
        with cy: vm = st.number_input("💧 السيولة (M)", format="%.2f", key="v83")
    if pm > 0:
        piv = (hm + lm + pm) / 3
        rs, ss = [(2*piv)-lm, pm*1.04, pm*1.06], [(2*piv)-hm, pm*0.96, pm*0.94]
        build_pro_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, piv, rs, ss)
