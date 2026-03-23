import streamlit as st
import requests
import pandas as pd

# ================== CONFIG ==================
st.set_page_config(page_title="EGX Sniper PRO", layout="wide")

WATCHLIST = ["TMGH","COMI","ETEL","SWDY","EFID","ATQA","ALCN","RMDA"]

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

ALL_STOCKS = WATCHLIST + ["ORAS","FWRY","AMOC","HELI","PHDC","MNHD","EKHO"]

# ================== STYLE ==================
st.markdown("""
<style>
body, .stApp {background-color: #0d1117; color: white;}
.card {background-color:#161b22; padding:20px; border-radius:15px; margin-bottom:15px;}
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
        r = requests.post(url, json=payload, timeout=10).json()
        d = r["data"][0]["d"]
        return float(d[0]), float(d[1]), float(d[2]), float(d[3])
    except:
        return None, None, None, None

# ================== INDICATORS ==================
def pivots(p, h, l):
    piv = (p + h + l) / 3
    s1 = (2 * piv) - h
    s2 = piv - (h - l)
    r1 = (2 * piv) - l
    r2 = piv + (h - l)
    return s1, s2, r1, r2

def rsi_fake(p, h, l):
    if h == l:
        return 50
    return ((p - l) / (h - l)) * 100

def liquidity(vol):
    if vol > 2_000_000:
        return "سيولة عالية"
    elif vol > 500_000:
        return "سيولة متوسطة"
    else:
        return "سيولة ضعيفة"

# ================== SIGNALS ==================
def reversal_signal(p, s1, r1, rsi):
    if p <= s1 * 1.02 and rsi < 30:
        return "🟢 إشارة ارتداد صاعد"
    if p >= r1 * 0.98 and rsi > 70:
        return "🔴 إشارة ارتداد هابط"
    return "لا توجد إشارة ارتداد"

def confirmation_signal(p, s1, r1, rsi):
    if p > r1 and rsi > 50:
        return "🟢 تأكيد شراء"
    if p < s1 and rsi < 50:
        return "🔴 تأكيد بيع"
    return "⚪ لا يوجد تأكيد"

# ================== REPORT ==================
def show_report(code, p, h, l, v):
    s1, s2, r1, r2 = pivots(p,h,l)
    rsi = rsi_fake(p,h,l)
    liq = liquidity(v)

    rev = reversal_signal(p,s1,r1,rsi)
    conf = confirmation_signal(p,s1,r1,rsi)

    st.markdown(f"""
    <div class="card">
    <h3>{code} - {COMPANIES.get(code,'')}</h3>
    💰 السعر الحالي: {p:.2f}<br>
    📉 RSI: {rsi:.1f}<br>
    🧱 الدعم: {s1:.2f} / {s2:.2f}<br>
    🚧 المقاومة: {r1:.2f} / {r2:.2f}<br>
    💧 السيولة: {liq}<br>
    <hr>
    🔄 {rev}<br>
    ⚡ {conf}<br>
    <hr>
    🎯 المضارب: مناسب قرب الدعم<br>
    🔁 السوينج: مراقبة الاتجاه<br>
    🏦 المستثمر: يعتمد على الاتجاه العام<br>
    <hr>
    📌 التوصية: انتظار<br>
    📝 ملحوظة للمحبوس: أقرب دعم {s1:.2f} ثم {s2:.2f}
    </div>
    """, unsafe_allow_html=True)

# ================== SCANNER ==================
def scanner():
    rows = []

    for s in ALL_STOCKS:
        p,h,l,v = get_data(s)
        if not p:
            continue

        s1, s2, r1, r2 = pivots(p,h,l)
        rsi = rsi_fake(p,h,l)
        liq = liquidity(v)

        near_support = abs(p - s1) / p * 100

        rows.append({
            "السهم": s,
            "السعر": round(p,2),
            "RSI": round(rsi,1),
            "الدعم": round(s1,2),
            "المقاومة": round(r1,2),
            "السيولة": liq,
            "قرب الدعم %": round(near_support,2)
        })

    return pd.DataFrame(rows)

# ================== UI ==================
st.title("🏹 EGX Sniper PRO")

tab1, tab2, tab3 = st.tabs(["📡 التحليل الآلي", "🛠️ التحليل اليدوي", "🚨 Scanner"])

# ---------- AUTO ----------
with tab1:
    code = st.text_input("ادخل كود السهم").upper()
    if code:
        p,h,l,v = get_data(code)
        if p:
            show_report(code,p,h,l,v)
        else:
            st.error("البيانات غير متاحة")

# ---------- MANUAL ----------
with tab2:
    p = st.number_input("السعر")
    h = st.number_input("أعلى سعر")
    l = st.number_input("أقل سعر")
    v = st.number_input("السيولة")
    if p > 0:
        show_report("MANUAL",p,h,l,v)

# ---------- SCANNER ----------
with tab3:
    st.subheader("🚨 Scanner السوق")

    df = scanner()

    option = st.radio("فلترة:", ["الكل","سوينج","مضاربة"])

    if option == "سوينج":
        df = df[
            (df["RSI"] >= 40) &
            (df["RSI"] <= 65) &
            (df["قرب الدعم %"] <= 2) &
            (df["السيولة"] != "سيولة ضعيفة")
        ]

    elif option == "مضاربة":
        df = df[
            (df["RSI"] > 70) &
            (df["السيولة"] == "سيولة عالية")
        ]

    st.dataframe(df, use_container_width=True)
