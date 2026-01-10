import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.parse
from datetime import datetime

# --- لو حبيت تستخدم investpy كبديل ---
try:
    import investpy
    HAS_INVESTING = True
except:
    HAS_INVESTING = False

st.set_page_config(page_title="EGX Live Sniper", layout="centered")

# --- CSS التنسيق ---
st.markdown("""
<style>
header, .main, .stApp {background-color: #0d1117 !important;}
.report-card {background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; direction: rtl; text-align: right; border: 1px solid #30363d; margin: 10px auto;}
.metric-box { background: #21262d; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #30363d; }
.indicator-on { color: #2ecc71; font-weight: bold; }
.indicator-off { color: #e74c3c; font-weight: bold; }
.wa-button { background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; display: block; text-decoration: none; margin-top: 15px; }
.white-text { color: #ffffff !important; }
.alert-up { background-color: #2ecc71; color: white; padding:5px; border-radius:5px; text-align:center; }
.alert-down { background-color: #e74c3c; color: white; padding:5px; border-radius:5px; text-align:center; }
</style>
""", unsafe_allow_html=True)

# --- قاعدة بيانات الأسماء ---
ARABIC_DB = {
    "SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم",
    "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري للمدفوعات",
    "BTFH": "بلتون المالية", "TMGH": "طلعت مصطفى", "SWDY": "السويدي إليكتريك",
    "ATQA": "عتاقة للصلب", "UNIT": "المتحدة للإسكان", "AMOC": "الإسكندرية للزيوت",
    "ORAS": "أوراسكوم", "EKHO": "القابضة الكويتية", "PHDC": "بالم هيلز", "JUFO": "جهينة"
}

st.markdown("<h1 style='text-align:center; color:white;'>📈 EGX Live Sniper</h1>", unsafe_allow_html=True)

u_input = st.text_input("🔍 ادخل كود السهم (مثلاً TMGH):").upper().strip()

# --- تحديث تلقائي كل دقيقة ---
st_autorefresh = st.experimental_singleton(lambda: st.experimental_rerun)
st_autorefresh(interval=60 * 1000)  # 60 ثانية

# --- جلب بيانات Yahoo ---
@st.cache_data(ttl=60)
def get_yahoo_data(symbol):
    try:
        ticker = symbol if symbol.endswith(".CA") else f"{symbol}.CA"
        df = yf.Ticker(ticker).history(period="1y")
        if df.empty: return None
        return df
    except:
        return None

# --- جلب بيانات Investing ---
@st.cache_data(ttl=60)
def get_investing_data(symbol):
    if not HAS_INVESTING: return None
    try:
        df = investpy.get_stock_historical_data(stock=symbol, country='egypt', from_date='01/01/2023', to_date=datetime.today().strftime('%d/%m/%Y'))
        if df.empty: return None
        return df
    except:
        return None

# --- بناء الكارت + تنبيهات ---
def build_card(name, sym, p, vol, rsi, sup, res, score, cl_p=0, m_h=0, h_d=0, l_d=0):
    wa_msg = f"🎯 تقرير: {name}\n💰 السعر: {p:.3f}\n⭐ التقييم: {score}/6\n🚀 هدف: {res:.2f}\n🛡️ دعم: {sup:.2f}"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
    trend_alert = "<div class='alert-up'>⬆️ صاعد</div>" if p > cl_p else "<div class='alert-down'>⬇️ هابط</div>"

    st.markdown(f"""
    <div class="report-card">
        <h2 style="text-align:center; color:white;">{name}</h2>
        <p style="text-align:center; color:#3498db;">({sym})</p>
        {trend_alert}
        <div style="display:flex; justify-content:space-around; margin:10px 0;">
            <div class="metric-box">💰 السعر<br><b class="white-text">{p:.3f}</b></div>
            <div class="metric-box">⭐ التقييم<br><b class="white-text">{score}/6</b></div>
            <div class="metric-box">📊 السيولة M<br><b class="white-text">{vol:.1f}</b></div>
        </div>
        <div style="margin-top:10px;">
            <p><span style="color:#3498db; font-weight:bold;">🚀 المقاومة:</span> <b class="white-text">{res:.3f}</b></p>
            <p><span style="color:#3498db; font-weight:bold;">🛡️ الدعم:</span> <b class="white-text">{sup:.3f}</b></p>
            <p style="text-align:center; color:#ff3b30; font-weight:bold; font-size:18px;">🛑 وقف الخسارة: {sup*0.98:.3f}</p>
        </div>
        <div style="background:#21262d; padding:10px; border-radius:8px; font-size:13px; border: 1px solid #30363d;">
            <div style="display:flex; justify-content:space-between;">
                <span class="white-text">🔝 أعلى يوم: <b>{h_d:.3f}</b></span>
                <span class="white-text">📉 أقل يوم: <b>{l_d:.3f}</b></span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:5px;">
                <span class="white-text">↩️ إغلاق أمس: <b>{cl_p:.3f}</b></span>
                <span class="white-text">🗓️ أعلى شهر: <b>{m_h:.3f}</b></span>
            </div>
        </div>
        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة التقرير عبر WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# --- معالجة الإدخال ---
if u_input:
    df = get_yahoo_data(u_input)
    source_used = "Yahoo"
    if df is None and HAS_INVESTING:
        df = get_investing_data(u_input)
        source_used = "Investing"

    if df is not None and len(df) > 20:
        df["EMA50"] = ta.ema(df["Close"], length=50)
        df["RSI"] = ta.rsi(df["Close"], length=14)
        last = df.iloc[-1]
        p, r = last["Close"], last["RSI"]
        v = (last['Volume']*p)/1_000_000 if "Volume" in last else 0
        s20, r20 = df["Low"].tail(20).min(), df["High"].tail(20).max()
        sc = 0
        if p > last["EMA50"]: sc +=1
        if r < 40: sc +=1
        build_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, v, r, s20, r20, sc, cl_p=df["Close"].iloc[-2], m_h=df["High"].tail(22).max(), h_d=last["High"], l_d=last["Low"])
        st.info(f"💡 البيانات مأخوذة من: {source_used}")
    else:
        st.warning("⚠️ البيانات غير متاحة حالياً، يرجى المحاولة لاحقاً أو الإدخال يدوياً.")
