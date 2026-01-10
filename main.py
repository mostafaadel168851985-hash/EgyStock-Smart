import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- تفتيح المدخلات اليدوية (ناصع جداً) ---
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    label p, .stMarkdown p { color: #ffffff !important; font-weight: bold !important; font-size: 16px !important; }
    input { background-color: #1e2732 !important; color: white !important; border: 1px solid #3498db !important; }
</style>
""", unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "TMGH": "طلعت مصطفى", "ATQA": "مصر الوطنية للصلب", "SWDY": "السويدي إليكتريك"}

st.title("📊 Smart Stock Analyzer")
u_input = st.text_input("🔍 ادخل كود السهم (مثلاً ATQA):").upper().strip()

def build_telegram_card(name, sym, p, hi, lo, cl, vol, piv, rs, ss):
    # رسالة الواتساب الكاملة
    wa_msg = (f"🎯 تقرير: {name} ({sym})\n💰 السعر: {p:.3f}\n🟡 الارتكاز: {piv:.3f}\n"
              f"🚀 م1: {rs[0]:.3f} | م2: {rs[1]:.3f}\n🛡️ د1: {ss[0]:.3f} | د2: {ss[1]:.3f}\n📊 سيولة: {vol:.1f}M")
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    # كود الكارت (تنسيق تليجرام الأصلي المعزول)
    card_html = f"""
    <div style="direction: rtl; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1e2732; border-radius: 15px; border: 1px solid #30363d; padding: 20px; color: white;">
        <h2 style="text-align: center; margin-bottom: 20px; color: #ffffff;">{name} ({sym})</h2>
        
        <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
            <div style="text-align: center; background: #0d1117; padding: 10px; border-radius: 10px; flex: 1; margin: 0 5px; border: 1px solid #3d444d;">
                <div style="color: #8b949e; font-size: 12px;">السعر</div>
                <div style="font-size: 18px; font-weight: bold; color: #ffffff;">{p:.3f}</div>
            </div>
            <div style="text-align: center; background: #0d1117; padding: 10px; border-radius: 10px; flex: 1; margin: 0 5px; border: 1px solid #3d444d;">
                <div style="color: #8b949e; font-size: 12px;">السيولة M</div>
                <div style="font-size: 18px; font-weight: bold; color: #ffffff;">{vol:.1f}</div>
            </div>
        </div>

        <div style="background: #0d1117; padding: 12px; border-radius: 10px; text-align: center; border: 1px solid #f1c40f; margin-bottom: 15px;">
            <span style="color: #f1c40f; font-weight: bold;">🟡 نقطة الارتكاز:</span> 
            <span style="font-size: 20px; font-weight: bold; color: white;"> {piv:.3f}</span>
        </div>

        <div style="display: flex; justify-content: space-between; gap: 10px;">
            <div style="flex: 1; background: #161b22; padding: 15px; border-radius: 12px; border-right: 4px solid #3498db;">
                <div style="color: #3498db; font-weight: bold; margin-bottom: 8px;">🚀 المقاومات</div>
                <div style="color: white; line-height: 1.6;">م1: {rs[0]:.3f}<br>م2: {rs[1]:.3f}<br>م3: {rs[2]:.3f}</div>
            </div>
            <div style="flex: 1; background: #161b22; padding: 15px; border-radius: 12px; border-right: 4px solid #e74c3c;">
                <div style="color: #e74c3c; font-weight: bold; margin-bottom: 8px;">🛡️ الدعوم</div>
                <div style="color: white; line-height: 1.6;">د1: {ss[0]:.3f}<br>د2: {ss[1]:.3f}<br>د3: {ss[2]:.3f}</div>
            </div>
        </div>

        <div style="background: #0d1117; padding: 10px; border-radius: 10px; margin-top: 15px; border: 1px solid #30363d; font-size: 13px; text-align: center; color: #8b949e;">
            🔝 أعلى: <span style="color:white">{hi:.3f}</span> | 📉 أدنى: <span style="color:white">{lo:.3f}</span> | 🔙 أمس: <span style="color:white">{cl:.3f}</span>
        </div>

        <a href="{wa_url}" target="_top" style="background: linear-gradient(90deg, #25D366, #128C7E); color: white; text-decoration: none; display: block; text-align: center; padding: 15px; border-radius: 10px; margin-top: 20px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 15px rgba(37,211,102,0.3);">
            📲 مشاركة التقرير عبر WhatsApp
        </a>
    </div>
    """
    # عرض الكارت بطريقة المكونات المعزولة لمنع الـ Error
    components.html(card_html, height=520, scrolling=False)

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
            build_telegram_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, piv, rs, ss)
            found = True
    except: pass

# --- الإدخال اليدوي (ناصع جداً) ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### 🛠️ الإدخال اليدوي")
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("💵 السعر الآن", format="%.3f", key="p79")
with c2: hm = st.number_input("🔝 أعلى اليوم", format="%.3f", key="h79")
with c3: lm = st.number_input("📉 أقل اليوم", format="%.3f", key="l79")

with st.expander("➕ بيانات إضافية للرسالة"):
    st.write("ادخل البيانات التالية لضمان دقة التقرير:")
    cx, cy = st.columns(2)
    with cx: clm = st.number_input("↩️ إغلاق أمس", format="%.3f", key="c79")
    with cy: vm = st.number_input("💧 السيولة (M)", format="%.2f", key="v79")

if pm > 0 and not found:
    piv = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*piv)-lm if lm > 0 else pm*1.02, pm*1.04, pm*1.06]
    ss = [(2*piv)-hm if hm > 0 else pm*0.98, pm*0.96, pm*0.94]
    build_telegram_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, piv, rs, ss)
