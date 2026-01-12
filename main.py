import streamlit as st
import requests
import time
import urllib.parse

# =======================
# CONFIG
# =======================
st.set_page_config(page_title="EGX Sniper Live", layout="centered")

WATCHLIST = ["TMGH", "COMI", "ETEL", "SWDY", "EFID"]

# =======================
# STYLE
# =======================
st.markdown("""
<style>
header, .main, .stApp { background-color: #0d1117 !important; }
h1,h2,h3,p,span,label { color: #ffffff !important; font-weight: bold; }
.card {
    background: #ffffff;
    color: #000000 !important;
    padding: 20px;
    border-radius: 15px;
    border: 3px solid #2ecc71;
    margin-top: 15px;
}
.card * { color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

# =======================
# DATA SOURCE (TradingView)
# =======================
@st.cache_data(ttl=10)
def get_live_data(symbol):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "symbols": {"tickers": [f"EGX:{symbol}"], "query": {"types": []}},
            "columns": ["close", "high", "low"]
        }
        r = requests.post(url, json=payload, timeout=10).json()
        d = r["data"][0]["d"]
        return float(d[0]), float(d[1]), float(d[2])
    except:
        return None, None, None

# =======================
# CALCULATIONS
# =======================
def calc_levels(p, h, l):
    piv = (p + h + l) / 3
    s1 = (2 * piv) - h
    s2 = piv - (h - l)
    r1 = (2 * piv) - l
    r2 = piv + (h - l)
    return s1, s2, r1, r2

# =======================
# REPORT
# =======================
def show_report(name, p, h, l):
    s1, s2, r1, r2 = calc_levels(p, h, l)
    stop = s2 * 0.99

    st.markdown(f"""
    <div class="card">
        <h3 style="text-align:center;">📊 {name}</h3>
        <p>💰 السعر الحالي: {p:.2f}</p>
        <p style="color:green;">🎯 الأهداف: {r1:.2f} | {r2:.2f}</p>
        <p style="color:orange;">🛡️ الدعوم: {s1:.2f} | {s2:.2f}</p>
        <p style="color:red;">🛑 وقف الخسارة: {stop:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

    wa = f"تحليل {name}\nسعر {p:.2f}\nأهداف {r1:.2f}-{r2:.2f}\nدعوم {s1:.2f}-{s2:.2f}"
    st.markdown(
        f'<a href="https://wa.me/?text={urllib.parse.quote(wa)}">📲 مشاركة واتساب</a>',
        unsafe_allow_html=True
    )

# =======================
# SCANNER
# =======================
def run_scanner():
    alerts = []
    for s in WATCHLIST:
        p, h, l = get_live_data(s)
        if p:
            s1, _, _, _ = calc_levels(p, h, l)
            if p <= s1 * 1.01:
                alerts.append(f"🚨 {s} قرب دعم {s1:.2f} | السعر {p:.2f}")
    return alerts

# =======================
# UI
# =======================
st.title("🏹 EGX Sniper – Live Radar")

tab1, tab2, tab3 = st.tabs(["📡 سعر لحظي", "🛠️ تحليل يدوي", "🚨 Scanner"])

with tab1:
    code = st.text_input("ادخل كود السهم").upper().strip()
    refresh = st.slider("تحديث كل (ثواني)", 5, 60, 15)

    if code:
        with st.spinner("⏳ جاري التحديث اللحظي..."):
            p, h, l = get_live_data(code)
            if p:
                show_report(code, p, h, l)
            else:
                st.error("فشل جلب الداتا")

        time.sleep(refresh)
        st.rerun()

with tab2:
    c1, c2, c3 = st.columns(3)
    p = c1.number_input("السعر", format="%.2f")
    h = c2.number_input("أعلى سعر", format="%.2f")
    l = c3.number_input("أقل سعر", format="%.2f")

    if p > 0:
        show_report("تحليل يدوي", p, h, l)

with tab3:
    st.subheader("📡 الأسهم القريبة من الدعم")
    alerts = run_scanner()

    if alerts:
        for a in alerts:
            st.error(a)
    else:
        st.success("✅ لا فرص حالياً")
