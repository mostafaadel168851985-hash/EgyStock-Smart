import streamlit as st
import requests
import pandas as pd

# ================== CONFIG ==================
st.set_page_config(page_title="EGX Sniper PRO", layout="wide")

WATCHLIST = ["TMGH","COMI","ETEL","SWDY","EFID","ATQA","ALCN","RMDA"]
ALL_STOCKS = WATCHLIST + ["ORAS","FWRY","AMOC","HELI","PHDC","MNHD","EKHO"]

COMPANIES = {
    "TMGH": "طلعت مصطفى",
    "COMI": "البنك التجاري الدولي",
    "ETEL": "المصرية للاتصالات",
    "SWDY": "السويدي",
    "EFID": "إيديتا",
    "ATQA": "عتاقة",
    "ALCN": "ألكون",
    "RMDA": "رمادا"
}

# ================== STYLE ==================
st.markdown("""
<style>

body, .stApp {
    background-color: #0d1117;
    color: #ffffff;
}

/* الكارت */
.card {
    background: #161b22;
    padding:25px;
    border-radius:20px;
    margin-bottom:20px;
    font-size:18px;
    line-height:1.8;
}

/* Tabs مودرن */
.stTabs [role="tab"] {
    background-color:#161b22;
    border-radius:12px;
    padding:10px 20px;
    margin-right:10px;
    font-weight:bold;
    color:#aaa !important;
}

.stTabs [aria-selected="true"] {
    background-color:#ff4b4b !important;
    color:white !important;
}

/* Radio */
div[role="radiogroup"] label {
    font-size:17px !important;
    color:white !important;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ================== DATA ==================
@st.cache_data(ttl=300)
def get_data(symbol):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "symbols": {"tickers": [f"EGX:{symbol}"], "query": {"types": []}},
            "columns": ["close", "high", "low", "volume"]
        }
        r = requests.post(url, json=payload).json()
        d = r["data"][0]["d"]
        return float(d[0]), float(d[1]), float(d[2]), float(d[3])
    except:
        return None, None, None, None

# ================== INDICATORS ==================
def pivots(p,h,l):
    piv = (p+h+l)/3
    s1 = (2*piv)-h
    s2 = piv-(h-l)
    r1 = (2*piv)-l
    r2 = piv+(h-l)
    return s1,s2,r1,r2

def rsi_fake(p,h,l):
    if h==l:
        return 50
    return ((p-l)/(h-l))*100

def liquidity(v):
    if v > 2_000_000:
        return "سيولة عالية"
    elif v > 500_000:
        return "سيولة متوسطة"
    else:
        return "سيولة ضعيفة"

# ================== REPORT ==================
def show_report(code,p,h,l,v):
    s1,s2,r1,r2 = pivots(p,h,l)
    rsi = rsi_fake(p,h,l)
    liq = liquidity(v)

    trader_score = min(100, 50 + (20 if rsi < 30 else 0))
    swing_score = min(100, 60 + (50 - abs(50 - rsi)))
    invest_score = 80 if p > s1 else 55

    st.markdown(f"""
    <div class="card">

    <h2>{code} - {COMPANIES.get(code,'')}</h2>

    💰 السعر: {p:.2f}<br>
    📉 RSI: {rsi:.1f}<br>

    🧱 الدعم: {s1:.2f} / {s2:.2f}<br>
    🚧 المقاومة: {r1:.2f} / {r2:.2f}<br>
    💧 السيولة: {liq}<br>

    <hr>

    🎯 <b>المضارب:</b> {trader_score}/100  
    ⚡ دخول: {round(s1+0.1,2)} | وقف خسارة: {round(s1-0.15,2)}<br>

    🔁 <b>السوينج:</b> {swing_score}/100  
    🔁 دخول: {round((s1+r1)/2,2)} | وقف خسارة: {round((s1+r1)/2-0.25,2)}<br>

    🏦 <b>المستثمر:</b> {invest_score}/100  
    🏦 دخول: {round((s1+s2)/2,2)} | وقف خسارة: {round(s2-0.25,2)}<br>

    <hr>

    📌 التوصية: <b>انتظار</b><br>

    📝 <b>ملحوظة للمحبوس:</b>  
    أقرب دعم {s1:.2f} ثم {s2:.2f}

    </div>
    """, unsafe_allow_html=True)

# ================== SCANNER ==================
def scanner():
    rows = []

    for s in ALL_STOCKS:
        p,h,l,v = get_data(s)
        if not p:
            continue

        s1,s2,r1,r2 = pivots(p,h,l)
        rsi = rsi_fake(p,h,l)
        liq = liquidity(v)

        dist = abs(p - s1) / p * 100

        if dist < 1:
            signal = "🔥 لاصق في الدعم"
        elif dist < 2:
            signal = "🟢 قريب من الدعم"
        else:
            signal = "⚪ بعيد"

        rows.append({
            "السهم": s,
            "السعر": round(p,2),
            "RSI": round(rsi,1),
            "الدعم": round(s1,2),
            "المقاومة": round(r1,2),
            "السيولة": liq,
            "وضع الدعم": signal
        })

    return pd.DataFrame(rows)

# ================== UI ==================
st.title("🏹 EGX Sniper PRO")

tab1,tab2,tab3 = st.tabs(["📡 التحليل الآلي","🛠️ التحليل اليدوي","🚨 Scanner"])

# ---------- AUTO ----------
with tab1:
    code = st.text_input("ادخل كود السهم").upper()
    if code:
        p,h,l,v = get_data(code)
        if p:
            show_report(code,p,h,l,v)

# ---------- MANUAL ----------
with tab2:
    p = st.number_input("السعر")
    h = st.number_input("أعلى سعر")
    l = st.number_input("أقل سعر")
    v = st.number_input("السيولة")

    if p>0:
        show_report("MANUAL",p,h,l,v)

# ---------- SCANNER ----------
with tab3:
    st.subheader("🚨 فلترة السوق")

    df = scanner()

    option = st.radio("اختر الفلتر:", ["الكل","سوينج","مضاربة"])

    if option == "سوينج":
        df = df[(df["RSI"]>=40)&(df["RSI"]<=65)]

    elif option == "مضاربة":
        df = df[(df["RSI"]>70)]

    st.dataframe(df, use_container_width=True)
