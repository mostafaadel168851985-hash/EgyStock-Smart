import streamlit as st
import requests
import pandas as pd
import numpy as np
import yfinance as yf
import urllib.parse

# ================== CONFIG ==================
st.set_page_config(page_title="EGX Sniper PRO", layout="wide")

WATCHLIST = ["TMGH", "COMI", "ETEL", "SWDY", "EFID", "ATQA", "ALCN", "RMDA"]

COMPANIES = {
    "TMGH": "طلعت مصطفى",
    "COMI": "البنك التجاري الدولي",
    "ETEL": "المصرية للاتصالات",
    "SWDY": "السويدي إليكتريك",
    "EFID": "إيديتا",
    "ATQA": "عتاقة",
    "ALCN": "ألكون",
    "RMDA": "رمادا"
}

# ================== STYLE ==================
st.markdown("""
<style>
body, .stApp {background-color:#0d1117; color:white;}
.card {background-color:#161b22; padding:20px; border-radius:15px; margin-bottom:20px;}
.whatsapp-btn {
    background:#25D366; padding:12px; border-radius:14px;
    text-align:center; color:white !important;
    font-weight:bold; text-decoration:none; display:block; margin-top:12px;
}
</style>
""", unsafe_allow_html=True)

# ================== DATA (TradingView) ==================
@st.cache_data(ttl=120)
def get_tv_data(symbol):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "symbols": {"tickers": [f"EGX:{symbol}"], "query": {"types": []}},
            "columns": ["close", "high", "low", "volume"]
        }
        r = requests.post(url, json=payload, timeout=10).json()
        d = r["data"][0]["d"]
        return float(d[0]), float(d[1]), float(d[2]), float(d[3])
    except:
        return None, None, None, None

# ================== DATA (Yahoo Finance) ==================
@st.cache_data(ttl=3600)
def get_history(symbol):
    try:
        df = yf.download(f"{symbol}.CA", period="1y", interval="1d", progress=False)
        return df
    except:
        return None

# ================== INDICATORS ==================
def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calc_macd(series):
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd.iloc[-1], signal.iloc[-1]

def pivots(p, h, l):
    piv = (p + h + l) / 3
    return (
        (2*piv)-h,
        piv-(h-l),
        (2*piv)-l,
        piv+(h-l)
    )

def liquidity(vol):
    if vol > 2_000_000: return "سيولة عالية"
    if vol > 500_000: return "سيولة متوسطة"
    return "سيولة ضعيفة"

# ================== AI ENGINE ==================
def ai_analysis(p, s1, s2, r1, r2, rsi, macd, macd_sig, ema200):
    trend = "صاعد" if p > ema200 else "هابط"
    macd_txt = "زخم صاعد" if macd > macd_sig else "زخم ضعيف"

    # Recommendation logic
    if p <= s1*1.02 and rsi < 35:
        rec = "شراء"
    elif rsi > 70 and p >= r1*0.98:
        rec = "بيع"
    else:
        rec = "انتظار"

    note = (
        f"السهم يتحرك داخل نطاق عرضي. "
        f"أقرب دعم {s1:.2f}, دعم أقوى {s2:.2f}. "
        f"طالما التداول أعلى هذه المناطق، يظل الاحتفاظ خيارًا ممكنًا مع المتابعة."
    )

    return rec, trend, macd_txt, note

# ================== REPORT ==================
def show_report(code):
    p,h,l,v = get_tv_data(code)
    if not p:
        st.error("البيانات غير متاحة")
        return

    s1,s2,r1,r2 = pivots(p,h,l)
    liq = liquidity(v)

    hist = get_history(code)
    if hist is None or len(hist) < 50:
        rsi = 50
        macd = macd_sig = 0
        ema200 = p
    else:
        rsi = round(calc_rsi(hist["Close"]).iloc[-1],1)
        macd, macd_sig = calc_macd(hist["Close"])
        ema200 = hist["Close"].ewm(span=200).mean().iloc[-1]

    rec, trend, macd_txt, note = ai_analysis(
        p,s1,s2,r1,r2,rsi,macd,macd_sig,ema200
    )

    st.markdown(f"""
<div class="card">
<h3>{code} - {COMPANIES.get(code,"")}</h3>

💰 السعر الحالي: {p:.2f}  
📉 RSI: {rsi}  
📊 MACD: {macd_txt}  
📈 EMA 200: الاتجاه {trend}  

🧱 الدعم: {s1:.2f} / {s2:.2f}  
🚧 المقاومة: {r1:.2f} / {r2:.2f}  
💧 السيولة: {liq}  

📌 التوصية: **{rec}**

📝 **ملحوظة للمحبوس:**  
{note}
</div>
""", unsafe_allow_html=True)

# ================== UI ==================
st.title("🏹 EGX Sniper PRO")
tab1, tab2 = st.tabs(["📡 التحليل الآلي", "🚨 Scanner"])

with tab1:
    code = st.text_input("ادخل كود السهم").upper().strip()
    if code:
        show_report(code)

with tab2:
    for s in WATCHLIST:
        show_report(s)
