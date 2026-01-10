import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS التنسيق (تصميم تليجرام الموحد) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d; margin: 15px auto;
    }
    .metric-box { background: #21262d; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #30363d; }
    .indicator-on { color: #2ecc71; font-weight: bold; }
    .indicator-off { color: #e74c3c; font-weight: bold; }
    .label-gold { color: #f1c40f; font-weight: bold; }
    .label-blue { color: #3498db; font-weight: bold; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; padding: 12px; border-radius: 10px;
        text-align: center; font-weight: bold; display: block; text-decoration: none; margin-top: 15px;
    }
    b, span, p, h2 { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# قاعدة بيانات الأسماء
ARABIC_DB = {
    "SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم",
    "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري للمدفوعات",
    "BTFH": "بلتون المالية", "TMGH": "مجموعة طلعت مصطفى", "SWDY": "السويدي إليكتريك",
    "ATQA": "مصر الوطنية للصلب", "UNIT": "المتحدة للإسكان", "AMOC": "إسكندرية للزيوت"
}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)

u_input = st.text_input("🔍 ادخل كود السهم (مثلاً TMGH):").upper().strip()

def build_card(name, sym, p, high, low, close_prev, vol, score, inds, p_data):
    wa_msg = f"🎯 تقرير {name}\n💰 السعر: {p:.2f}\n⭐ التقييم: {score}/6"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
    
    pivot, rs, ss = p_data

    st.markdown(f"""
    <div class="report-card">
        <h2 style="text-align:center;">{name} ({sym})</h2>
        <div style="display:flex; justify-content:space-around; margin:15px 0;">
            <div class="metric-box">💰 السعر<br><b>{p:.3f}</b></div>
            <div class="metric-box">⭐ التقييم<br><b>{score}/6</b></div>
            <div class="metric-box">📊 السيولة M<br><b>{vol:.1f}</b></div>
        </div>

        <div style="background:#0d1117; padding:12px; border-radius:10px; border:1px dashed #30363d; margin-bottom:15px;">
            <p style="text-align:center; color:#3498db !important; font-weight:bold; margin-bottom:5px;">🔍 الفحص الفني الذكي:</p>
            <div style="display:flex; justify-content:space-between; font-size:14px;">
                <span>📈 EMA50: <b class="{'indicator-on' if inds['c1'] else 'indicator-off'}">{'إيجابي' if inds['c1'] else 'سلبي'}</b></span>
                <span>💧 الزخم: <b class="{'indicator-on' if inds['c2'] else 'indicator-off'}">{'إيجابي' if inds['c2'] else 'سلبي'}</b></span>
                <span>🔥 الاتجاه: <b class="{'indicator-on' if inds['c4'] else 'indicator-off'}">{'صاعد' if inds['c4'] else 'هابط'}</b></span>
            </div>
        </div>

        <div style="background:#21262d; padding:10px; border-radius:8px; margin-bottom:10px; text-align:center;">
            <p style="margin:0;"><span class="label-gold">🟡 نقطة الارتكاز:</span> <b>{pivot:.3f}</b></p>
        </div>

        <div style="display:flex; justify-content:space-between;">
            <div style="width:48%;">
                <p class="label-blue">🚀 المقاومات:</p>
                <p>م 1: <b>{rs[0]:.3f}</b><br>م 2: <b>{rs[1]:.3f}</b><br>م 3: <b>{rs[2]:.3f}</b></p>
            </div>
            <div style="width:48%;">
                <p class="label-blue">🛡️ الدعوم:</p>
                <p>د 1: <b>{ss[0]:.3f}</b><br>د 2: <b>{ss[1]:.3f}</b><br>د 3: <b>{ss[2]:.3f}</b></p>
            </div>
        </div>

        <div style="background:#0d1117; padding:10px; border-radius:8px; font-size:13px; margin-top:10px; border: 1px solid #444;">
            <div style="display:flex; justify-content:space-between;">
                <span>🔝 أعلى: {high:.3f}</span>
                <span>📉 أدنى: {low:.3f}</span>
                <span>🔙 أمس: {close_prev:.3f}</span>
            </div>
        </div>
        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة عبر WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# --- محرك التحليل ---
res_data = None
if u_input:
    try:
        ticker = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        df = yf.Ticker(ticker).history(period="1y")
        if not df.empty:
            l = df.iloc[-1]
            p, hi, lo, cl = l["Close"], l["High"], l["Low"], df["Close"].iloc[-2]
            
            # حسابات البيفوت
            pivot = (hi + lo + p) / 3
            rs = [(2*pivot)-lo, pivot+(hi-lo), hi+2*(pivot-lo)]
            ss = [(2*pivot)-hi, pivot-(hi-lo), lo-2*(hi-pivot)]
            
            # حسابات المؤشرات (تأمين ضد الـ Error)
            ema50 = df["Close"].rolling(window=min(50, len(df))).mean().iloc[-1]
            inds = {"c1": p > ema50, "c2": p > cl, "c4": p > df["Close"].iloc[-3] if len(df)>3 else True}
            sc = sum([inds["c1"], inds["c2"], inds["c4"]]) + 2
            
            build_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, sc, inds, (pivot, rs, ss))
            res_data = True
    except: pass

# --- اليدوي ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h4 style='color:white; text-align:center;'>🛠️ الإدخال اليدوي</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("السعر الآن:", format="%.3f", key="p_manual")
with c2: hm = st.number_input("أعلى سعر:", format="%.3f", key="h_manual")
with c3: lm = st.number_input("أقل سعر:", format="%.3f", key="l_manual")

with st.expander("📊 بيانات إضافية"):
    c4, c5 = st.columns(2)
    with c4: clm = st.number_input("إغلاق أمس:", format="%.3f", key="cl_manual")
    with c5: vm = st.number_input("السيولة (M):", format="%.2f", key="v_manual")

if pm > 0 and not res_data:
    pivot = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*pivot)-lm if lm>0 else pm*1.02, pivot+(hm-lm) if hm>0 else pm*1.04, pm*1.06]
    ss = [(2*pivot)-hm if hm>0 else pm*0.98, pivot-(hm-lm) if hm>0 else pm*0.96, pm*0.94]
    build_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, 3, {"c1":True, "c2":True, "c4":True}, (pivot, rs, ss))
