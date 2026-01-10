import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer PRO", layout="centered")

# --- CSS التنسيق (ألوان بيضاء واضحة وتصميم تليجرام) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d; margin: 10px auto;
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
    b, span, p { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري", "BTFH": "بلتون", "TMGH": "طلعت مصطفى", "SWDY": "السويدي"}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل كود السهم (مثلاً SVCE):").upper().strip()

def calculate_pivots(high, low, close):
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    r2 = pivot + (high - low)
    r3 = high + 2 * (pivot - low)
    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    s3 = low - 2 * (high - pivot)
    return pivot, r1, r2, r3, s1, s2, s3

def build_full_report(name, sym, p, high, low, close_prev, vol, score, inds, r_list, s_list, pivot):
    wa_msg = f"🎯 تقرير {name}\n💰 السعر: {p:.2f}\n⭐ التقييم: {score}/6\n📈 ارتكاز: {pivot:.2f}"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    st.markdown(f"""
    <div class="report-card">
        <h2 style="text-align:center;">{name} ({sym})</h2>
        <div style="display:flex; justify-content:space-around; margin:10px 0;">
            <div class="metric-box">💰 السعر<br><b>{p:.3f}</b></div>
            <div class="metric-box">⭐ التقييم<br><b>{score}/6</b></div>
            <div class="metric-box">📊 السيولة<br><b>{vol:.1f}M</b></div>
        </div>

        <div style="background:#0d1117; padding:10px; border-radius:10px; border:1px dashed #30363d; margin-bottom:15px;">
            <p style="text-align:center; color:#3498db !important; font-weight:bold;">🔍 التحليل الذكي للمؤشرات:</p>
            <div style="display:flex; justify-content:space-between; font-size:13px;">
                <span>📈 EMA50: <b class="{'indicator-on' if inds['c1'] else 'indicator-off'}">{'إيجابي' if inds['c1'] else 'سلبي'}</b></span>
                <span>💧 MACD: <b class="{'indicator-on' if inds['c2'] else 'indicator-off'}">{'إيجابي' if inds['c2'] else 'سلبي'}</b></span>
                <span>🔥 الاتجاه: <b class="{'indicator-on' if inds['c4'] else 'indicator-off'}">{'صاعد' if inds['c4'] else 'هابط'}</b></span>
            </div>
        </div>

        <div style="background:#21262d; padding:12px; border-radius:10px; margin-bottom:10px;">
            <p style="margin:0;"><span class="label-gold">🟡 نقطة الارتكاز:</span> <b>{pivot:.3f}</b></p>
        </div>

        <div style="display:flex; justify-content:space-between;">
            <div style="width:48%;">
                <p class="label-blue">🚀 المقاومات:</p>
                <p>م 1: <b>{r_list[0]:.3f}</b></p>
                <p>م 2: <b>{r_list[1]:.3f}</b></p>
                <p>م 3: <b>{r_list[2]:.3f}</b></p>
            </div>
            <div style="width:48%;">
                <p class="label-blue">🛡️ الدعوم:</p>
                <p>د 1: <b>{s_list[0]:.3f}</b></p>
                <p>د 2: <b>{s_list[1]:.3f}</b></p>
                <p>د 3: <b>{s_list[2]:.3f}</b></p>
            </div>
        </div>

        <div style="background:#0d1117; padding:10px; border-radius:8px; font-size:13px; margin-top:10px; border:1px solid #444;">
            <div style="display:flex; justify-content:space-between;">
                <span>🔝 أعلى: {high:.3f}</span>
                <span>📉 أدنى: {low:.3f}</span>
                <span>🔙 إغلاق أمس: {close_prev:.3f}</span>
            </div>
        </div>
        <a href="{wa_url}" target="_blank" class="wa-button">📲 إرسال التقرير الشامل للواتساب</a>
    </div>
    """, unsafe_allow_html=True)

if u_input:
    try:
        ticker = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        df = yf.Ticker(ticker).history(period="1y")
        if not df.empty:
            l = df.iloc[-1]
            p, hi, lo, cl = l["Close"], l["High"], l["Low"], df["Close"].iloc[-2]
            # حسابات البيفوت (نفس شغل الملف)
            pv, r1, r2, r3, s1, s2, s3 = calculate_pivots(hi, lo, p)
            # حسابات السكور
            df["EMA50"] = ta.ema(df["Close"], length=50)
            macd = ta.macd(df["Close"])
            inds = {"c1": p > df["EMA50"].iloc[-1], "c2": macd.iloc[-1][0] > macd.iloc[-1][2], "c4": p > cl}
            sc = sum([inds["c1"], inds["c2"], inds["c4"]]) + 1
            build_full_report(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, sc, inds, [r1, r2, r3], [s1, s2, s3], pv)
    except: st.error("خطأ في جلب البيانات.")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>🛠️ الإدخال اليدوي الكامل</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("السعر الآن:", format="%.3f")
with c2: hm = st.number_input("أعلى سعر:", format="%.3f")
with c3: lm = st.number_input("أقل سعر:", format="%.3f")
with st.expander("بيانات إضافية"):
    clm = st.number_input("إغلاق أمس:", format="%.3f")
    vm = st.number_input("السيولة (M):", format="%.2f")

if pm > 0:
    pv, r1, r2, r3, s1, s2, s3 = calculate_pivots(hm if hm>0 else pm, lm if lm>0 else pm, pm)
    build_full_report(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, 3, {"c1":True, "c2":True, "c4":True}, [r1, r2, r3], [s1, s2, s3], pv)
