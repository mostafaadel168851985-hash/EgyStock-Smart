import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS التنسيق (ألوان قوية وزرار Smart) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; padding: 25px; border-radius: 20px; 
        direction: rtl; text-align: right; border: 1px solid #30363d; margin: 15px auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .metric-container { display: flex; justify-content: space-around; margin-bottom: 20px; }
    .metric-box { background: #21262d; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #3d444d; flex: 1; margin: 0 5px; }
    .metric-label { color: #8b949e; font-size: 14px; margin-bottom: 5px; }
    .metric-value { color: #ffffff !important; font-size: 20px; font-weight: bold; }
    .label-gold { color: #f1c40f !important; font-weight: bold; }
    .label-blue { color: #58a6ff !important; font-weight: bold; }
    .white-bright { color: #ffffff !important; font-weight: bold; }
    
    /* الزرار المودرن */
    .wa-button {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important; padding: 15px 25px; border-radius: 12px;
        text-align: center; font-weight: bold; display: block; text-decoration: none; 
        margin-top: 20px; transition: 0.3s; box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3);
        font-size: 16px; border: none;
    }
    .wa-button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37, 211, 102, 0.5); }
    </style>
    """, unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري", "BTFH": "بلتون", "TMGH": "طلعت مصطفى", "SWDY": "السويدي", "ATQA": "مصر الوطنية للصلب", "UNIT": "المتحدة للإسكان"}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 كود السهم (مثلاً TMGH):").upper().strip()

def build_modern_card(name, sym, p, high, low, close_prev, vol, score, pivot, rs, ss):
    # رسالة واتساب كاملة ومنظمة
    wa_msg = (f"🎯 تقرير: {name} ({sym})\n"
              f"💰 السعر الحالي: {p:.3f}\n"
              f"⭐ التقييم: {score}/6\n"
              f"🟡 الارتكاز: {pivot:.3f}\n"
              f"🚀 هدف (م1): {rs[0]:.3f}\n"
              f"🛡️ دعم (د1): {ss[0]:.3f}\n"
              f"🛑 وقف: {ss[0]*0.98:.3f}\n"
              f"📊 سيولة: {vol:.1f}M")
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    st.markdown(f"""
    <div class="report-card">
        <h2 style="text-align:center; color:white; margin-bottom:20px;">{name}</h2>
        
        <div class="metric-container">
            <div class="metric-box"><div class="metric-label">السعر الحالي</div><div class="metric-value">{p:.3f}</div></div>
            <div class="metric-box"><div class="metric-label">التقييم</div><div class="metric-value">{score}/6</div></div>
            <div class="metric-box"><div class="metric-label">السيولة M</div><div class="metric-value">{vol:.1f}</div></div>
        </div>

        <div style="background:#0d1117; padding:15px; border-radius:12px; border:1px solid #30363d; margin-bottom:15px; text-align:center;">
            <p style="margin:0;"><span class="label-gold">🟡 نقطة الارتكاز المحورية:</span> <b class="white-bright" style="font-size:20px;">{pivot:.3f}</b></p>
        </div>

        <div style="display:flex; justify-content:space-between; gap:15px;">
            <div style="flex:1; background:#161b22; padding:15px; border-radius:12px; border-right:4px solid #58a6ff;">
                <p class="label-blue" style="margin-bottom:10px;">🚀 مستويات المقاومة</p>
                <p class="white-bright">م 1: {rs[0]:.3f}</p>
                <p class="white-bright">م 2: {rs[1]:.3f}</p>
                <p class="white-bright">م 3: {rs[2]:.3f}</p>
            </div>
            <div style="flex:1; background:#161b22; padding:15px; border-radius:12px; border-right:4px solid #f85149;">
                <p style="color:#f85149; font-weight:bold; margin-bottom:10px;">🛡️ مستويات الدعم</p>
                <p class="white-bright">د 1: {ss[0]:.3f}</p>
                <p class="white-bright">د 2: {ss[1]:.3f}</p>
                <p class="white-bright">د 3: {ss[2]:.3f}</p>
            </div>
        </div>

        <div style="background:#0d1117; padding:12px; border-radius:10px; margin-top:15px; border:1px solid #30363d;">
            <div style="display:flex; justify-content:space-between; font-size:14px;">
                <span class="white-bright">🔝 أعلى سعر: {high:.3f}</span>
                <span class="white-bright">📉 أدنى سعر: {low:.3f}</span>
                <span class="white-bright">🔙 إغلاق أمس: {close_prev:.3f}</span>
            </div>
        </div>

        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة التقرير الذكي عبر WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# --- محرك البحث ---
found = False
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
            build_modern_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, 4, pivot, rs, ss)
            found = True
    except: pass

# --- لوحة اليدوي المودرن ---
st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color:white; text-align:center;'>🛠️ لوحة الإدخال اليدوي</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("💵 السعر الآن:", format="%.3f", key="p_v71")
with c2: hm = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="h_v71")
with c3: lm = st.number_input("📉 أقل اليوم:", format="%.3f", key="l_v71")

with st.expander("📊 بيانات إضافية"):
    c4, c5 = st.columns(2)
    with c4: clm = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="cl_v71")
    with c5: vm = st.number_input("💧 السيولة (M):", format="%.2f", key="v_v71")

if pm > 0 and not found:
    pivot = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*pivot)-lm if lm>0 else pm*1.02, pm*1.04, pm*1.06]
    ss = [(2*pivot)-hm if hm>0 else pm*0.98, pm*0.96, pm*0.94]
    build_modern_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, 3, pivot, rs, ss)
