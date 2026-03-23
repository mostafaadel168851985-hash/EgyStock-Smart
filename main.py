import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="EGX Sniper PRO", layout="wide")

# ================== STOCKS ==================
ALL_STOCKS = [
    "COMI","TMGH","ETEL","SWDY","EFID","ATQA","ALCN","RMDA",
    "ORAS","FWRY","AMOC","HELI","PHDC","MNHD","EKHO"
]

# ================== STYLE ==================
st.markdown("""
<style>
body, .stApp {background-color: #0d1117; color: white;}
.card {background-color:#161b22; padding:20px; border-radius:15px;}
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

# ================== CALCULATIONS ==================
def pivots(p, h, l):
    piv = (p + h + l) / 3
    s1 = (2 * piv) - h
    r1 = (2 * piv) - l
    return s1, r1

def rsi_fake(p, h, l):
    if h == l:
        return 50
    return ((p - l) / (h - l)) * 100

def liquidity(v):
    if v > 2_000_000:
        return "عالية"
    elif v > 500_000:
        return "متوسطة"
    else:
        return "ضعيفة"

# ================== SCANNER ==================
def build_scanner():
    rows = []

    for s in ALL_STOCKS:
        p,h,l,v = get_data(s)
        if not p:
            continue

        s1, r1 = pivots(p,h,l)
        rsi = rsi_fake(p,h,l)
        liq = liquidity(v)

        near_support = abs(p - s1) / p * 100
        near_resistance = abs(p - r1) / p * 100

        rows.append({
            "السهم": s,
            "السعر": round(p,2),
            "RSI": round(rsi,1),
            "الدعم": round(s1,2),
            "المقاومة": round(r1,2),
            "السيولة": liq,
            "قرب الدعم %": round(near_support,2),
            "قرب المقاومة %": round(near_resistance,2)
        })

    return pd.DataFrame(rows)

# ================== FILTERS ==================
def filter_swing(df):
    return df[
        (df["RSI"] >= 40) &
        (df["RSI"] <= 65) &
        (df["قرب الدعم %"] <= 2) &
        (df["السيولة"] != "ضعيفة")
    ].sort_values(by="قرب الدعم %")

def filter_scalping(df):
    return df[
        (df["RSI"] > 70) &
        (df["السيولة"] == "عالية")
    ].sort_values(by="RSI", ascending=False)

# ================== UI ==================
st.title("🏹 EGX Sniper PRO")

tab1, tab2 = st.tabs(["🚨 Scanner", "📊 تحليل سهم"])

# ---------- SCANNER ----------
with tab1:
    st.subheader("📊 فلترة السوق")

    df = build_scanner()

    option = st.radio(
        "اختار نوع الفرص:",
        ["الكل", "سوينج", "مضاربة"]
    )

    if option == "سوينج":
        df = filter_swing(df)
    elif option == "مضاربة":
        df = filter_scalping(df)

    st.dataframe(df, use_container_width=True)

# ---------- SINGLE STOCK ----------
with tab2:
    code = st.text_input("ادخل كود السهم").upper()

    if code:
        p,h,l,v = get_data(code)

        if p:
            s1, r1 = pivots(p,h,l)
            rsi = rsi_fake(p,h,l)
            liq = liquidity(v)

            st.markdown(f"""
            <div class="card">
            <h3>{code}</h3>
            💰 السعر: {p:.2f}<br>
            📉 RSI: {rsi:.1f}<br>
            🧱 الدعم: {s1:.2f}<br>
            🚧 المقاومة: {r1:.2f}<br>
            💧 السيولة: {liq}
            </div>
            """, unsafe_allow_html=True)

        else:
            st.error("البيانات غير متاحة")
