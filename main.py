import streamlit as st
import requests
import urllib.parse
import time

# ================= CONFIG =================
st.set_page_config(page_title="EGX Sniper PRO", layout="centered")

WATCHLIST = ["TMGH", "COMI", "ETEL", "SWDY", "EFID"]

# ================= STYLE =================
st.markdown("""
<style>
header, .main, .stApp { background-color: #0d1117 !important; }
h1,h2,h3,p,span,label { color: #ffffff !important; font-weight: bold; }
.card {
    background: #ffffff;
    color: #000000 !important;
    padding: 20px;
    border-radius: 18px;
    border: 3px solid #3498db;
    margin-top: 15px;
}
.card * { color: #000000 !important; }
.badge {
    padding: 6px 12px;
    border-radius: 12px;
    font-weight: bold;
}
.up { background:#2ecc71; color:white; }
.down { background:#e74c3c; color:white; }
.flat { background:#f1c40f; color:black; }
</style>
""", unsafe_allow_html=True)

# ================= DATA =================
@st.cache_data(ttl=10)
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

# ================= INDICATORS =================
def calc_pivot(p, h, l):
    piv = (p + h + l) / 3
    s1 = (2 * piv) - h
    s2 = piv - (h - l)
    r1 = (2 * piv) - l
    r2 = piv + (h - l)
    return s1, s2, r1, r2

def calc_trend(p, h, l):
    mid = (h + l) / 2
    if p > mid * 1.01:
        return "صاعد", "up"
    elif p < mid * 0.99:
        return "هابط", "down"
    else:
        return "عرضي", "flat"

def calc_rsi(p, h, l):
    rng = h - l
    if rng == 0:
        return 50
    return max(0, min(100, ((p - l) / rng) * 100))

def liquidity_score(vol):
    if vol > 2_000_000:
        return "سيولة عالية"
    elif vol > 500_000:
        return "سيولة متوسطة"
    else:
        return "سيولة ضعيفة"

# ================= RECOMMENDATION =================
def recommendation(p, s1, r1, trend, rsi):
    reasons = []
    rec = "انتظار"

    if p <= s1 * 1.02 and rsi < 35:
        rec = "شراء"
        reasons.append("السعر قرب من دعم قوي")
        reasons.append("RSI منخفض (تشبع بيع)")
    elif p >= r1 * 0.98 and rsi > 70:
        rec = "بيع"
        reasons.append("السعر قرب مقاومة")
        reasons.append("RSI مرتفع (تشبع شراء)")
    else:
        reasons.append("لا توجد إشارة واضحة")

    reasons.append(f"الاتجاه العام: {trend}")
    return rec, reasons

# ================= REPORT =================
def show_report(name, p, h, l, vol):
    s1, s2, r1, r2 = calc_pivot(p, h, l)
    trend, trend_cls = calc_trend(p, h, l)
    rsi = calc_rsi(p, h, l)
    liq = liquidity_score(vol)
    rec, reasons = recommendation(p, s1, r1, trend, rsi)

    wa_msg = f"""
تحليل {name}
السعر: {p:.2f}
الاتجاه: {trend}
RSI: {rsi:.1f}
السيولة: {liq}

المضارب:
شراء قرب {s1:.2f}
هدف {r1:.2f}
وقف {s2*0.99:.2f}

المستثمر:
الاحتفاظ طالما أعلى {s2:.2f}

التوصية: {rec}
"""

    st.markdown(f"""
    <div class="card">
        <h3 style="text-align:center;">📊 {name}</h3>
        <p>💰 السعر: {p:.2f}</p>
        <p>📈 الاتجاه: <span class="badge {trend_cls}">{trend}</span></p>
        <p>⚡ RSI: {rsi:.1f}</p>
        <p>💧 السيولة: {liq}</p>
        <hr>
        <p><b>🎯 المضارب:</b><br>
        شراء قرب {s1:.2f}<br>
        هدف {r1:.2f}<br>
        وقف {s2*0.99:.2f}</p>
        <p><b>🏦 المستثمر:</b><br>
        الاحتفاظ طالما أعلى {s2:.2f}</p>
        <hr>
        <p><b>📌 التوصية:</b> {rec}</p>
        <ul>
            {''.join(f"<li>{r}</li>" for r in reasons)}
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<a href="https://wa.me/?text={urllib.parse.quote(wa_msg)}">📲 مشاركة التحليل على واتساب</a>',
        unsafe_allow_html=True
    )

# ================= SCANNER =================
def scanner():
    hits = []
    for s in WATCHLIST:
        p, h, l, v = get_data(s)
        if p:
            s1, _, _, _ = calc_pivot(p, h, l)
            rsi = calc_rsi(p, h, l)
            if p <= s1 * 1.02 and rsi < 40:
                hits.append(f"🚨 {s} فرصة مضاربة | سعر {p:.2f}")
    return hits

# ================= UI =================
st.title("🏹 EGX Sniper PRO")

tab1, tab2, tab3 = st.tabs(["📡 تحليل لحظي", "🛠️ يدوي", "🚨 Scanner"])

with tab1:
    code = st.text_input("ادخل كود السهم").upper().strip()
    refresh = st.slider("تحديث (ثواني)", 5, 60, 15)

    if code:
        p, h, l, v = get_data(code)
        if p:
            show_report(code, p, h, l, v)
        else:
            st.error("فشل جلب البيانات")

        time.sleep(refresh)
        st.rerun()

with tab2:
    c1, c2, c3, c4 = st.columns(4)
    p = c1.number_input("السعر", format="%.2f")
    h = c2.number_input("أعلى", format="%.2f")
    l = c3.number_input("أقل", format="%.2f")
    v = c4.number_input("السيولة")

    if p > 0:
        show_report("تحليل يدوي", p, h, l, v)

with tab3:
    st.subheader("📡 فرص مضاربية قريبة من الدعم")
    res = scanner()
    if res:
        for r in res:
            st.error(r)
    else:
        st.success("لا فرص حالياً")
