import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

# إعداد الصفحة
st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS (تفتيح الخطوط وإلغاء التظليل) ---
st.markdown("""
<style>
    /* تفتيح عام */
    body, .main, .stApp { background-color: #0d1117 !important; color: white !important; }
    
    /* جعل خانات الإدخال واضحة جداً */
    .stNumberInput label, .stTextInput label { color: #ffffff !important; font-size: 16px !important; font-weight: bold !important; }
    input { background-color: #1e2732 !important; color: white !important; border: 1px solid #3498db !important; }

    /* تنسيق الكارت */
    .report-card {
        background-color: #1e2732; padding: 20px; border-radius: 15px; border: 2px solid #30363d;
        direction: rtl; text-align: right; margin-bottom: 20px;
    }
    .white-text { color: #ffffff !important; font-weight: bold; }
    .blue-text { color: #58a6ff !important; font-weight: bold; }
    .gold-text { color: #f1c40f !important; font-weight: bold; }
    
    .wa-btn {
        background: linear-gradient(135deg, #25D366, #128C7E); color: white !important;
        padding: 12px; border-radius: 10px; text-align: center; display: block;
        text-decoration: none; font-weight: bold; margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "TMGH": "طلعت مصطفى", "ATQA": "مصر الوطنية للصلب"}

st.markdown("<h1 style='text-align:center;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 كود السهم (اختياري):").upper().strip()

def build_card(name, sym, p, hi, lo, cl, vol, pivot, rs, ss, score=4):
    # رسالة الواتساب الشاملة
    wa_msg = (f"🎯 تقرير: {name} ({sym})\n💰 السعر: {p:.3f}\n⭐ التقييم: {score}/6\n"
              f"🟡 الارتكاز: {pivot:.3f}\n🚀 م1: {rs[0]:.3f}\n🛡️ د1: {ss[0]:.3f}\n📊 سيولة: {vol:.1f}M")
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    # بناء الكارت بقطع منفصلة لضمان عدم حدوث Error
    with st.container():
        st.markdown(f"""
        <div class="report-card">
            <h2 style="text-align:center; color:white;">{name} ({sym})</h2>
            <div style="display:flex; justify-content:space-around; margin-bottom:15px;">
                <div style="text-align:center;">💰 السعر<br><span style="font-size:20px;">{p:.3f}</span></div>
                <div style="text-align:center;">⭐ التقييم<br><span style="font-size:20px;">{score}/6</span></div>
                <div style="text-align:center;">📊 السيولة M<br><span style="font-size:20px;">{vol:.1f}</span></div>
            </div>
            
            <div style="background:#0d1117; padding:10px; border-radius:10px; text-align:center; border:1px solid #f1c40f; margin-bottom:15px;">
                <span class="gold-text">🟡 الارتكاز المحوري:</span> <span style="font-size:22px;">{pivot:.3f}</span>
            </div>

            <div style="display:flex; justify-content:space-between; gap:10px;">
                <div style="flex:1; background:#161b22; padding:10px; border-radius:10px; border-right:4px solid #58a6ff;">
                    <span class="blue-text">🚀 المقاومات:</span><br>
                    م1: {rs[0]:.3f}<br>م2: {rs[1]:.3f}<br>م3: {rs[2]:.3f}
                </div>
                <div style="flex:1; background:#161b22; padding:10px; border-radius:10px; border-right:4px solid #f85149;">
                    <span style="color:#f85149; font-weight:bold;">🛡️ الدعوم:</span><br>
                    د1: {ss[0]:.3f}<br>د2: {ss[1]:.3f}<br>د3: {ss[2]:.3f}
                </div>
            </div>

            <div style="background:#0d1117; padding:10px; border-radius:10px; margin-top:15px; border:1px solid #30363d; text-align:center;">
                <span class="white-text">🔝 أعلى: {hi:.3f} | 📉 أدنى: {lo:.3f} | 🔙 أمس: {cl:.3f}</span>
            </div>
            
            <a href="{wa_url}" target="_blank" class="wa-btn">📲 مشاركة التقرير عبر WhatsApp</a>
        </div>
        """, unsafe_allow_html=True)

# --- محرك البيانات ---
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

# --- المدخلات اليدوية ---
st.markdown("<h4 style='text-align:center;'>🛠️ لوحة الإدخال اليدوي</h4>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1: p_m = st.number_input("السعر الآن", format="%.3f", key="p1")
with col2: h_m = st.number_input("أعلى سعر", format="%.3f", key="h1")
with col3: l_m = st.number_input("أقل سعر", format="%.3f", key="l1")

with st.expander("➕ بيانات إضافية للتحليل"):
    c4, c5 = st.columns(2)
    with c4: cl_m = st.number_input("إغلاق أمس", format="%.3f", key="c1")
    with c5: v_m = st.number_input("السيولة (M)", format="%.2f", key="v1")

if p_m > 0 and not found:
    piv_m = (h_m + l_m + p_m) / 3 if h_m > 0 else p_m
    rs_m = [(2*piv_m)-l_m if l_m>0 else p_m*1.02, p_m*1.04, p_m*1.06]
    ss_m = [(2*piv_m)-h_m if h_m>0 else p_m*0.98, p_m*0.96, p_m*0.94]
    build_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", p_m, h_m, l_m, cl_m, v_m, piv_m, rs_m, ss_m, score=3)
