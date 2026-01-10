import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS التنسيق (ألوان بيضاء واضحة جداً) ---
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
    "ATQA": "مصر الوطنية للصلب - عتاقة", "UNIT": "المتحدة للإسكان", "AMOC": "الإسكندرية للزيوت"
}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)

u_input = st.text_input("🔍 ادخل كود السهم (اختياري):").upper().strip()

def calculate_pivots(high, low, close):
    pivot = (high + low + close) / 3
    r1, r2, r3 = (2*pivot)-low, pivot+(high-low), high+2*(pivot-low)
    s1, s2, s3 = (2*pivot)-high, pivot-(high-low), low-2*(high-pivot)
    return pivot, [r1, r2, r3], [s1, s2, s3]

def build_card(name, sym, p, high, low, close_prev, vol, score, inds, pivots_data):
    pivot, rs, ss = pivots_data
    wa_msg = f"🎯 تقرير {name}\n💰 السعر: {p:.2f}\n⭐ التقييم: {score}/6\n📈 ارتكاز: {pivot:.2f}"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

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
                <span>💧 MACD: <b class="{'indicator-on' if inds['c2'] else 'indicator-off'}">{'إيجابي' if inds['c2'] else 'سلبي'}</b></span>
                <span>🔥 الاتجاه: <b class="{'indicator-on' if inds['c4'] else 'indicator-off'}">{'صاعد' if inds['c4'] else 'هابط'}</b></span>
            </div>
        </div>

        <div style="background:#21262d; padding:10px; border-radius:8px; margin-bottom:10px;">
            <p style="margin:0; text-align:center;"><span class="label-gold">🟡 نقطة الارتكاز:</span> <b>{pivot:.3f}</b></p>
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
        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة التقرير عبر WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# --- محاولة البحث الآلي (محمية) ---
auto_success = False
if u_input:
    try:
        ticker = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        df = yf.Ticker(ticker).history(period="1y")
        if not df.empty and len(df) > 10:
            l = df.iloc[-1]
            p, hi, lo, cl = l["Close"], l["High"], l["Low"], df["Close"].iloc[-2]
            # حسابات المؤشرات
            ema = ta.ema(df["Close"], length=min(50, len(df)))
            macd = ta.macd(df["Close"])
            inds = {"c1": p > ema.iloc[-1] if ema is not None else True, 
                    "c2": macd.iloc[-1][0] > macd.iloc[-1][2] if macd is not None else True, 
                    "c4": p > cl}
            sc = sum([inds["c1"], inds["c2"], inds["c4"]]) + 1
            pivots = calculate_pivots(hi, lo, p)
            build_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, sc, inds, pivots)
            auto_success = True
    except:
        pass

# --- لوحة الإدخال اليدوي ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h4 style='color:white; text-align:center;'>🛠️ التحليل اليدوي المطور</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("💵 السعر الآن:", format="%.3f", key="pm_k")
with c2: hm = st.number_input("🔝 أعلى سعر:", format="%.3f", key="hm_k")
with c3: lm = st.number_input("📉 أقل سعر:", format="%.3f", key="lm_k")

with st.expander("📊 بيانات إضافية (اختياري)"):
    c4, c5 = st.columns(2)
    with c4: clm = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="clm_k")
    with c5: vm = st.number_input("💧 السيولة (M):", format="%.2f", key="vm_k")

if pm > 0 and not auto_success:
    pivots_m = calculate_pivots(hm if hm>0 else pm, lm if lm>0 else pm, pm)
    build_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, 3, {"c1":True, "c2":True, "c4":True}, pivots_m)
