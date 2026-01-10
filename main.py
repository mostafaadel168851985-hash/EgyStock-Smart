import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS (تفتيح نهائي وشامل) ---
st.markdown("""
<style>
    body, .main, .stApp { background-color: #0d1117 !important; }
    label, p, span { color: #ffffff !important; font-weight: bold !important; font-size: 16px !important; }
    input { background-color: #1e2732 !important; color: white !important; border: 1px solid #3498db !important; }
    .report-card {
        background-color: #1e2732; padding: 25px; border-radius: 15px; border: 1px solid #30363d;
        direction: rtl; text-align: right; margin-bottom: 20px; line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "TMGH": "طلعت مصطفى", "ATQA": "مصر الوطنية للصلب"}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل كود السهم:").upper().strip()

def build_card(name, sym, p, hi, lo, cl, vol, pivot, rs, ss, score=4):
    # رسالة الواتساب
    wa_msg = f"🎯 تقرير: {name}\n💰 السعر: {p:.3f}\n🟡 الارتكاز: {pivot:.3f}\n🚀 م1: {rs[0]:.3f}\n🛡️ د1: {ss[0]:.3f}\n📊 سيولة: {vol:.1f}M"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    # بناء الكارت بطريقة التجميع الآمنة
    card_top = """
    <div class="report-card">
        <h2 style="text-align:center; color:white;">{} ({})</h2>
        <div style="display:flex; justify-content:space-around; margin:15px 0;">
            <div style="text-align:center; color:white;">💰 السعر<br><span style="font-size:22px;">{:.3f}</span></div>
            <div style="text-align:center; color:white;">⭐ التقييم<br><span style="font-size:22px;">{}/6</span></div>
            <div style="text-align:center; color:white;">📊 السيولة<br><span style="font-size:22px;">{:.1f}M</span></div>
        </div>
        
        <div style="background:#0d1117; padding:10px; border-radius:10px; text-align:center; border:1px solid #f1c40f; margin-bottom:15px;">
            <span style="color:#f1c40f; font-weight:bold;">🟡 الارتكاز المحوري:</span> <span style="font-size:22px; color:white;">{:.3f}</span>
        </div>

        <div style="display:flex; justify-content:space-between; gap:10px;">
            <div style="flex:1; background:#161b22; padding:10px; border-radius:10px; border-right:4px solid #58a6ff; color:white;">
                <span style="color:#58a6ff; font-weight:bold;">🚀 المقاومات:</span><br>
                م1: {:.3f}<br>م2: {:.3f}<br>م3: {:.3f}
            </div>
            <div style="flex:1; background:#161b22; padding:10px; border-radius:10px; border-right:4px solid #f85149; color:white;">
                <span style="color:#f85149; font-weight:bold;">🛡️ الدعوم:</span><br>
                د1: {:.3f}<br>د2: {:.3f}<br>د3: {:.3f}
            </div>
        </div>

        <div style="background:#0d1117; padding:10px; border-radius:10px; margin-top:15px; border:1px solid #30363d; text-align:center; color:white;">
            🔝 أعلى: {:.3f} | 📉 أدنى: {:.3f} | 🔙 أمس: {:.3f}
        </div>
        
        <a href="{}" target="_blank" style="background: linear-gradient(135deg, #25D366, #128C7E); color: white !important; padding: 12px; border-radius: 10px; text-align: center; display: block; text-decoration: none; font-weight: bold; margin-top: 15px;">📲 مشاركة عبر WhatsApp</a>
    </div>
    """
    # تعبئة البيانات في القالب بشكل آمن
    full_html = card_top.format(name, sym, p, score, vol, pivot, rs[0], rs[1], rs[2], ss[0], ss[1], ss[2], hi, lo, cl, wa_url)
    st.markdown(full_html, unsafe_allow_html=True)

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
            build_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, piv, rs, ss, score=5)
            found = True
    except: pass

# --- لوحة اليدوي ---
st.markdown("<h4 style='text-align:center; color:white;'>🛠️ الإدخال اليدوي</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("💵 السعر الآن", format="%.3f", key="pm74")
with c2: hm = st.number_input("🔝 أعلى سعر", format="%.3f", key="hm74")
with c3: lm = st.number_input("📉 أقل سعر", format="%.3f", key="lm74")

with st.expander("➕ بيانات إضافية"):
    c4, c5 = st.columns(2)
    with c4: clm = st.number_input("↩️ إغلاق أمس", format="%.3f", key="cm74")
    with c5: vm = st.number_input("💧 السيولة (M)", format="%.2f", key="vm74")

if pm > 0 and not found:
    piv = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*piv)-lm if lm > 0 else pm*1.02, pm*1.04, pm*1.06]
    ss = [(2*piv)-hm if hm > 0 else pm*0.98, pm*0.96, pm*0.94]
    build_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, piv, rs, ss, score=3)
