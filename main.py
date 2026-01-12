import streamlit as st
import requests
import urllib.parse
import time

# ================== CONFIG ==================
st.set_page_config(page_title="EGX Sniper PRO", layout="wide")

WATCHLIST = ["TMGH", "COMI", "ETEL", "SWDY", "EFID"]

COMPANIES = {
    "TMGH": "طلعت مصطفى",
    "COMI": "البنك التجاري الدولي",
    "ETEL": "المصرية للاتصالات",
    "SWDY": "السويدي إليكتريك",
    "EFID": "إيديتا"
}

# ================== STYLE ==================
st.markdown("""
<style>
body, .stApp, .main { background-color: #0d1117; color: #ffffff;}
h1,h2,h3,p,span,label,li { color: #ffffff !important; font-weight: bold; }

.card {
    background: #161b22;
    color: #ffffff !important;
    padding: 22px;
    border-radius: 22px;
    margin-top: 15px;
    border: 2px solid #3498db;
}
.badge {padding:6px 14px; border-radius:14px; font-weight:bold;}
.up { background:#2ecc71; color:white; }
.down { background:#e74c3c; color:white; }
.flat { background:#f1c40f; color:black; }

.whatsapp-btn {
    background: linear-gradient(135deg, #25D366, #128C7E);
    padding: 15px;
    border-radius: 16px;
    text-align: center;
    color: white !important;
    font-size: 18px;
    font-weight: bold;
    display: block;
    margin-top: 18px;
}
</style>
""", unsafe_allow_html=True)

# ================== DATA ==================
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

# ================== INDICATORS ==================
def pivots(p, h, l):
    piv = (p + h + l) / 3
    s1 = (2 * piv) - h
    s2 = piv - (h - l)
    r1 = (2 * piv) - l
    r2 = piv + (h - l)
    return s1, s2, r1, r2

def trend_status(p, h, l):
    mid = (h + l) / 2
    if p > mid * 1.01:
        return "صاعد", "up"
    elif p < mid * 0.99:
        return "هابط", "down"
    else:
        return "عرضي", "flat"

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

# ================== SCORE & AI ==================
def score_trader(rsi_val, price, s1):
    score = 50
    if rsi_val < 30: score += 20
    if abs(price - s1)/s1 < 0.02: score += 15
    return min(score, 100)

def score_swing(rsi_val):
    return min(100, 60 + (50 - abs(50 - rsi_val)))

def score_invest(price, s2):
    return 80 if price > s2 else 55

def ai_comment_trader(price, s1):
    return f"⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f} مع الالتزام بوقف الخسارة."

def ai_comment_swing():
    return "🔁 السهم في حركة تصحيح داخل اتجاه عام، راقب الارتداد."

def ai_comment_invest():
    return "🏦 الاتجاه طويل الأجل إيجابي طالما السعر أعلى الدعم الثاني."

# ================== RECOMMENDATION ==================
def make_recommendation(p, s1, r1, trend, rsi):
    reasons = []
    rec = "انتظار"
    if p <= s1 * 1.02 and rsi < 40:
        rec = "شراء"
        reasons += ["قرب من دعم قوي", "RSI منخفض"]
    elif p >= r1 * 0.98 and rsi > 70:
        rec = "بيع"
        reasons += ["قرب من مقاومة", "RSI مرتفع"]
    reasons.append(f"الاتجاه العام: {trend}")
    return rec, reasons

# ================== REPORT ==================
def show_report(code, p, h, l, vol):
    company = COMPANIES.get(code, "")
    s1, s2, r1, r2 = pivots(p, h, l)
    trend, cls = trend_status(p, h, l)
    rsi = rsi_fake(p, h, l)
    liq = liquidity(vol)

    trader_score = score_trader(rsi, p, s1)
    swing_score = score_swing(rsi)
    invest_score = score_invest(p, s2)

    # AI Comments
    ai_trader = ai_comment_trader(p, s1)
    ai_swing = ai_comment_swing()
    ai_invest = ai_comment_invest()

    # WhatsApp message
    wa_msg = f"""
📊 تحليل {code} - {company}
💰 السعر: {p:.2f}
📈 الاتجاه: {trend}
⚡ RSI: {rsi:.1f}
💧 السيولة: {liq}

🎯 مضارب: {trader_score}/100
🔁 سوينج: {swing_score}/100
🏦 مستثمر: {invest_score}/100

📝 تعليقات AI:
- {ai_trader}
- {ai_swing}
- {ai_invest}
"""

    # Display card
    st.markdown(f"""
    <div class="card">
        <h3 style="text-align:center;">📊 {code} – {company}</h3>
        <p>💰 السعر: {p:.2f}</p>
        <p>📈 الاتجاه: <span class="badge {cls}">{trend}</span></p>
        <p>⚡ RSI: {rsi:.1f}</p>
        <p>💧 السيولة: {liq}</p>
        <hr>
        <p><b>🎯 المضارب:</b> {trader_score}/100 | {ai_trader}</p>
        <p><b>🔁 سوينج:</b> {swing_score}/100 | {ai_swing}</p>
        <p><b>🏦 مستثمر:</b> {invest_score}/100 | {ai_invest}</p>
        <hr>
        <p><b>📌 التوصية:</b> {make_recommendation(p, s1, r1, trend, rsi)[0]}</p>
    </div>
    """, unsafe_allow_html=True)

    # WhatsApp button
    wa_url = "https://wa.me/?text=" + urllib.parse.quote(wa_msg)
    st.markdown(f'<a class="whatsapp-btn" href="{wa_url}" target="_blank">📲 مشاركة التحليل على واتساب</a>', unsafe_allow_html=True)

# ================== SCANNER ==================
def scanner():
    results = []
    for s in WATCHLIST:
        p, h, l, v = get_data(s)
        if p:
            s1, _, r1, _ = pivots(p, h, l)
            rsi = rsi_fake(p, h, l)
            if p <= s1 * 1.02 and rsi < 40:
                results.append(
                    f"🚨 {s} ({COMPANIES.get(s,'')}) | سعر {p:.2f} | دعم {s1:.2f} | هدف {r1:.2f}"
                )
    return results

# ================== UI ==================
st.title("🏹 EGX Sniper PRO - Dark Mode")

tab1, tab2, tab3 = st.tabs(["📡 التحليل الآلي", "🛠️ التحليل اليدوي", "🚨 Scanner"])

with tab1:
    code = st.text_input("ادخل كود السهم").upper().strip()
    refresh = st.slider("تحديث تلقائي (ثواني)", 5, 60, 15)

    if code:
        p, h, l, v = get_data(code)
        if p:
            show_report(code, p, h, l, v)
        else:
            st.warning("⚠️ البيانات للسهم غير متاحة، استخدم التحليل اليدوي")

        time.sleep(refresh)
        st.experimental_rerun()

with tab2:
    c1, c2, c3, c4 = st.columns(4)
    p = c1.number_input("السعر", format="%.2f")
    h = c2.number_input("أعلى", format="%.2f")
    l = c3.number_input("أقل", format="%.2f")
    v = c4.number_input("عدد الأسهم المتداولة")

    if p > 0:
        show_report("MANUAL", p, h, l, v)

with tab3:
    st.subheader("📡 فرص مضاربية قرب الدعم")
    res = scanner()
    if res:
        for r in res:
            st.error(r)
    else:
        st.success("لا توجد فرص حالياً")
