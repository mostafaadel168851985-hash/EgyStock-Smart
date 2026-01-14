import streamlit as st
import requests
import urllib.parse

# ================== CONFIG ==================
st.set_page_config(page_title="EGX Sniper PRO", layout="wide")

WATCHLIST = ["TMGH", "COMI", "ETEL", "SWDY", "EFID", "ATQA"]

COMPANIES = {
    "TMGH": "طلعت مصطفى",
    "COMI": "البنك التجاري الدولي",
    "ETEL": "المصرية للاتصالات",
    "SWDY": "السويدي إليكتريك",
    "EFID": "إيديتا",
    "ATQA": "عتاقة"
}

# ================== STYLE ==================
st.markdown("""
<style>
body, .stApp, .main {background-color: #0d1117; color: #ffffff;}
h1,h2,h3,p,label,span {color: #ffffff;}
.stButton>button {background-color:#25D366;color:white;font-weight:bold;}
.stTabs button {background-color:#161b22;color:white;font-weight:bold;}
.card {background-color:#161b22; padding:20px; border-radius:15px; margin-bottom:20px;}
.score {font-size:16px; font-weight:bold; color:#00ff99;}
.whatsapp-btn {
    background: linear-gradient(135deg,#25D366,#128C7E);
    padding:12px;
    border-radius:14px;
    text-align:center;
    color:white !important;
    font-weight:bold;
    text-decoration:none;
    display:block;
    margin-top:12px;
}
</style>
""", unsafe_allow_html=True)

# ================== DATA ==================
@st.cache_data(ttl=300)
def get_data(symbol):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "symbols": {"tickers": [f"EGX:{symbol.upper()}"], "query": {"types": []}},
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

# ================== REVERSAL & CONFIRMATION ==================
def reversal_signal(p, s1, r1, rsi):
    if p <= s1 * 1.02 and rsi < 30:
        return "🟢 إشارة ارتداد صاعد", "up"
    if p >= r1 * 0.98 and rsi > 70:
        return "🔴 إشارة ارتداد هابط", "down"
    return "⚪ لا توجد إشارة ارتداد", None

def confirmation_signal(p, s1, r1, rsi):
    if p > r1 and rsi > 50:
        return "🟢 تأكيد شراء بعد كسر مقاومة", "buy"
    if p < s1 and rsi < 50:
        return "🔴 تأكيد بيع بعد كسر دعم", "sell"
    return "⚪ لا يوجد تأكيد", None

# ================== AI SMART COMMENTS ==================
def ai_comment_trader(p, s1):
    return f"⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f} مع الالتزام بوقف الخسارة."

def ai_comment_swing(p, h, l):
    mid = (h+l)/2
    return f"🔁 حركة تصحيح داخل اتجاه عام قرب {mid:.2f}, مراقبة الارتداد مطلوبة."

def ai_comment_invest(p, s2):
    return f"🏦 الاتجاه طويل الأجل إيجابي طالما أعلى {s2:.2f}."

def calc_score(p, s1, s2, h, l):
    trader = min(100, 50 + (20 if p - s1 < 0.02*s1 else 0))
    swing = min(100, 60 + (50 - abs(50 - rsi_fake(p,h,l))))
    invest = 80 if p > (h+l)/2 else 55
    return trader, swing, invest

# ================== REPORT ==================
def show_report(code, p, h, l, v):
    s1, s2, r1, r2 = pivots(p,h,l)
    rsi = rsi_fake(p,h,l)
    liq = liquidity(v)

    rev_txt, rev_type = reversal_signal(p, s1, r1, rsi)
    conf_txt, conf_type = confirmation_signal(p, s1, r1, rsi)
    rec = "انتظار"
    if conf_type == "buy":
        rec = "شراء"
    elif conf_type == "sell":
        rec = "بيع"

    trader_score, swing_score, invest_score = calc_score(p, s1, s2, h, l)

    trader_comment = ai_comment_trader(p, s1)
    swing_comment = ai_comment_swing(p, h, l)
    invest_comment = ai_comment_invest(p, s2)

    st.markdown(f"""
    <div class="card">
    <h3>{code} - {COMPANIES.get(code,'')}</h3>
    💰 السعر الحالي: {p:.2f}<br>
    📉 RSI: {rsi:.1f}<br>
    🧱 الدعم: {s1:.2f} / {s2:.2f}<br>
    🚧 المقاومة: {r1:.2f} / {r2:.2f}<br>
    💧 السيولة: {liq}<br>
    <hr>
    🎯 <b>مضارب</b> ({trader_score}/100): {trader_comment} دخول {s1:.2f}, وقف خسارة {s1*0.97:.2f}<br>
    🔁 <b>سوينج</b> ({swing_score}/100): {swing_comment} دخول {(h+l)/2:.2f}, وقف خسارة {s2:.2f}<br>
    🏦 <b>مستثمر</b> ({invest_score}/100): {invest_comment} دخول {s2:.2f}, وقف خسارة {s2*0.95:.2f}<br>
    <hr>
    🔄 {rev_txt}<br>
    ⚡ {conf_txt}<br>
    <hr>
    📌 التوصية: <b>{rec}</b>
    </div>
    """, unsafe_allow_html=True)

# ================== SCANNER ==================
def scanner():
    results = []
    for s in WATCHLIST:
        p,h,l,v = get_data(s)
        if not p:
            continue
        s1, s2, r1, r2 = pivots(p,h,l)
        rsi = rsi_fake(p,h,l)
        liq = liquidity(v)

        rev_txt, rev_type = reversal_signal(p, s1, r1, rsi)
        conf_txt, conf_type = confirmation_signal(p, s1, r1, rsi)
        trader_comment = ai_comment_trader(p,s1)
        swing_comment = ai_comment_swing(p,h,l)
        invest_comment = ai_comment_invest(p,s2)

        results.append(f"{s} | السعر {p:.2f} | دعم {s1:.2f}/{s2:.2f} | مقاومة {r1:.2f}/{r2:.2f} | RSI {rsi:.1f} | {liq} | {rev_txt} | {conf_txt} | ⚡ المضارب: {trader_comment} | 🔁 سوينج: {swing_comment} | 🏦 مستثمر: {invest_comment}")

    return results

# ================== UI ==================
st.title("🏹 EGX Sniper PRO")

tab1, tab2, tab3 = st.tabs(["📡 التحليل الآلي", "🛠️ التحليل اليدوي", "🚨 Scanner"])

with tab1:
    code = st.text_input("ادخل كود السهم").upper().strip()
    if code:
        p,h,l,v = get_data(code)
        if p:
            show_report(code,p,h,l,v)
        else:
            st.error("البيانات غير متاحة")

with tab2:
    p = st.number_input("السعر", format="%.2f")
    h = st.number_input("أعلى سعر", format="%.2f")
    l = st.number_input("أقل سعر", format="%.2f")
    v = st.number_input("السيولة")
    if p > 0:
        show_report("MANUAL",p,h,l,v)

with tab3:
    st.subheader("🚨 إشارات الأسهم")
    res = scanner()
    if res:
        for r in res:
            st.info(r)
    else:
        st.success("لا توجد إشارات حالياً")
