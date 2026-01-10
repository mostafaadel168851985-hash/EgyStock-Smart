import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS التنسيق القوي (تفتيح الخطوط تماماً) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    
    /* تفتيح خطوط الإدخال اليدوي */
    label, p, span, .stMarkdown { color: #ffffff !important; font-weight: 500 !important; }
    input { background-color: #1e2732 !important; color: white !important; border: 1px solid #3498db !important; }
    
    .report-card {
        background-color: #1e2732; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d; margin-bottom: 20px;
    }
    .metric-box { background: #0d1117; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #3d444d; }
    .white-title { color: #ffffff !important; font-size: 24px; font-weight: bold; text-align: center; display: block; }
    .white-value { color: #ffffff !important; font-size: 18px; font-weight: bold; }
    .label-blue { color: #58a6ff !important; font-weight: bold; }
    .label-gold { color: #f1c40f !important; font-weight: bold; }
    
    .wa-button {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important; padding: 15px; border-radius: 12px;
        text-align: center; font-weight: bold; display: block; text-decoration: none; 
        margin-top: 15px; font-size: 16px; border: none; box-shadow: 0 4px 15px rgba(37,211,102,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري", "BTFH": "بلتون", "TMGH": "طلعت مصطفى", "SWDY": "السويدي", "ATQA": "مصر الوطنية للصلب"}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)

u_input = st.text_input("🔍 كود السهم (مثلاً TMGH):").upper().strip()

def build_card(name, sym, p, hi, lo, cl, vol, pivot, rs, ss):
    # رسالة واتساب كاملة 100%
    wa_msg = (f"🎯 تقرير: {name} ({sym})\n💰 السعر: {p:.3f}\n🟡 الارتكاز: {pivot:.3f}\n"
              f"🚀 م1: {rs[0]:.3f} | م2: {rs[1]:.3f}\n🛡️ د1: {ss[0]:.3f} | د2: {ss[1]:.3f}\n"
              f"📊 سيولة: {vol:.1f}M")
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    # بناء الكارت بـ HTML بسيط جداً لمنع الـ Error
    st.markdown(f"""
    <div class="report-card">
        <span class="white-title">{name} ({sym})</span>
        <hr style="border-color:#30363d;">
        
        <div style="display:flex; justify-content:space-around; margin-bottom:15px;">
            <div class="metric-box"><span style="color:#aaa;">السعر</span><br><span class="white-value">{p:.3f}</span></div>
            <div class="metric-box"><span style="color:#aaa;">السيولة M</span><br><span class="white-value">{vol:.1f}</span></div>
        </div>

        <div style="background:#0d1117; padding:10px; border-radius:10px; text-align:center; margin-bottom:15px; border:1px solid #f1c40f;">
            <span class="label-gold">🟡 الارتكاز المحوري:</span> <span class="white-value" style="font-size:20px;">{pivot:.3f}</span>
        </div>

        <div style="display:flex; justify-content:space-between; gap:10px;">
            <div style="flex:1; background:#161b22; padding:10px; border-radius:10px; border-right:4px solid #58a6ff;">
                <span class="label-blue">🚀 المقاومات</span><br>
                م1: {rs[0]:.3f}<br>م2: {rs[1]:.3f}<br>م3: {rs[2]:.3f}
            </div>
            <div style="flex:1; background:#161b22; padding:10px; border-radius:10px; border-right:4px solid #f85149;">
                <span style="color:#f85149; font-weight:bold;">🛡️ الدعوم</span><br>
                د1: {ss[0]:.3f}<br>د2: {ss[1]:.3f}<br>د3: {ss[2]:.3f}
            </div>
        </div>

        <div style="background:#0d1117; padding:10px; border-radius:10px; margin-top:15px; font-size:14px; text-align:center; border:1px solid #30363d;">
            🔝 أعلى: {hi:.3f} | 📉 أدنى: {lo:.3f} | 🔙 أمس: {cl:.3f}
        </div>

        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة عبر WhatsApp</a>
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
            piv = (hi + lo + p) / 3
            rs = [(2*piv)-lo, piv+(hi-lo), hi+2*(piv-lo)]
            ss = [(2*piv)-hi, piv-(hi-lo), lo-2*(hi-piv)]
            build_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, piv, rs, ss)
            found = True
    except: pass

# --- اللوحة اليدوية (منورة) ---
st.markdown("<h4 style='text-align:center;'>🛠️ الإدخال اليدوي</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("السعر الآن", format="%.3f", key="p_72")
with c2: hm = st.number_input("أعلى سعر", format="%.3f", key="h_72")
with c3: lm = st.number_input("أقل سعر", format="%.3f", key="l_72")

with st.expander("➕ بيانات إضافية"):
    c4, c5 = st.columns(2)
    with c4: clm = st.number_input("إغلاق أمس", format="%.3f", key="cl_72")
    with c5: vm = st.number_input("السيولة (M)", format="%.2f", key="v_72")

if pm > 0 and not found:
    piv = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*piv)-lm if lm>0 else pm*1.02, pm*1.04, pm*1.06]
    ss = [(2*piv)-hm if hm>0 else pm*0.98, pm*0.96, pm*0.94]
    build_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, piv, rs, ss)
