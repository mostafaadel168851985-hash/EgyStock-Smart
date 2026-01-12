import streamlit as st
import requests
import urllib.parse

# ================== CONFIG ==================
st.set_page_config(page_title="🏹 EGX Sniper PRO", layout="wide")

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
header, .main, .stApp { background-color: #0d1117 !important; color:white !important; }
h1,h2,h3,p,span,label,li { color:#ffffff !important; font-weight:bold; }

.stTabs [role="tablist"] button {
    background-color:#0d1117 !important;
    color:white !important;
    font-weight:bold;
    border-radius:8px 8px 0 0;
    border: 1px solid #444;
    margin-right:2px;
}
.stTabs [role="tablist"] button[aria-selected="true"] {
    background-color:#161b22 !important;
    color:white !important;
    font-weight:bold;
}

.card { background:#161b22; color:white !important; padding:20px; border-radius:15px; margin-bottom:20px; border:1px solid #444; }
.score { font-size:24px; font-weight:bold; color:#00ff99; }
.whatsapp-btn { background: linear-gradient(135deg,#25D366,#128C7E); padding:12px; border-radius:14px; text-align:center; color:white !important; font-weight:bold; text-decoration:none; display:block; margin-top:12px; }
.stMarkdown div p, .stMarkdown div span, .stMarkdown div li { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ================== DATA ==================
@st.cache_data(ttl=600)
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

def liquidity(vol, price):
    value = vol * price
    if value > 2_000_000:
        return "سيولة عالية"
    elif value > 500_000:
        return "سيولة متوسطة"
    else:
        return "سيولة ضعيفة"

# ================== SCORES ==================
def score_trader(rsi_val, price, support):
    score = 50
    if rsi_val < 30: score += 20
    if abs(price - support)/support < 0.02: score += 15
    return min(score,100)

def score_swing(rsi_val):
    return min(100, 60 + (50 - abs(50 - rsi_val)))

def score_invest(price, ma50):
    return 80 if price > ma50 else 55

# ================== AI COMMENTS ==================
def ai_comment_trader(price, s1):
    return f"⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f} مع الالتزام بوقف الخسارة."

def ai_comment_swing():
    return "🔁 السهم في حركة تصحيح داخل اتجاه عام، مراقبة الارتداد مطلوبة."

def ai_comment_invest():
    return "🏦 الاتجاه طويل الأجل إيجابي طالما السعر أعلى المتوسط 50 يوم."

# ================== RECOMMENDATION ==================
def make_recommendation(p, s1, r1, rsi):
    if p <= s1*1.02 and rsi < 40:
        return "شراء"
    elif p >= r1*0.98 and rsi > 70:
        return "بيع"
    else:
        return "انتظار"

# ================== SHOW REPORT ==================
def show_report(code, p, h, l, vol):
    company = COMPANIES.get(code, "")
    s1, s2, r1, r2 = pivots(p,h,l)
    trend, cls = trend_status(p,h,l)
    rsi = rsi_fake(p,h,l)
    liq = liquidity(vol,p)
    rec = make_recommendation(p,s1,r1,rsi)
    ma50 = (p+h+l)/3
    trader_score = score_trader(rsi,p,s1)
    swing_score = score_swing(rsi)
    invest_score = score_invest(p,ma50)

    wa_msg = f"""
تحليل {code} - {company}
💰 السعر: {p:.2f}
📈 الاتجاه: {trend}
⚡ RSI: {rsi:.1f}
💧 السيولة: {liq}
🧱 الدعم: {s1:.2f}/{s2:.2f}
🚧 المقاومة: {r1:.2f}/{r2:.2f}
🎯 مضارب: {trader_score}/100
🔁 سوينج: {swing_score}/100
🏦 مستثمر: {invest_score}/100
📌 التوصية: {rec}
"""

    st.markdown(f"""
    <div class="card">
        <h3 style="text-align:center;">📊 {code} – {company}</h3>
        💰 السعر: {p:.2f}<br>
        📈 الاتجاه: {trend}<br>
        ⚡ RSI: {rsi:.1f}<br>
        💧 السيولة: {liq}<br>
        🧱 الدعم: {s1:.2f}/{s2:.2f}<br>
        🚧 المقاومة: {r1:.2f}/{r2:.2f}<br>
        🎯 مضارب: {trader_score}/100<br>
        🔁 سوينج: {swing_score}/100<br>
        🏦 مستثمر: {invest_score}/100<br>
        📌 التوصية: {rec}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<a class="whatsapp-btn" href="https://wa.me/?text={urllib.parse.quote(wa_msg)}">📲 مشاركة التحليل على واتساب</a>',
        unsafe_allow_html=True
    )

# ================== SCANNER ==================
def scanner():
    results = []
    for s in WATCHLIST:
        p,h,l,v = get_data(s)
        if p:
            s1,s2,r1,r2 = pivots(p,h,l)
            rsi = rsi_fake(p,h,l)
            rec = make_recommendation(p,s1,r1,rsi)
            liq = liquidity(v,p)
            results.append(
                f"🚨 {s} ({COMPANIES.get(s,'')}) | سعر {p:.2f} | دعم {s1:.2f}/{s2:.2f} | مقاومة {r1:.2f}/{r2:.2f} | سيولة: {liq} | توصية: {rec}"
            )
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
            st.error("لا توجد بيانات للسهم، استخدم التحليل اليدوي")

with tab2:
    c1,c2,c3,c4 = st.columns(4)
    p = c1.number_input("سعر اليوم",format="%.2f")
    h = c2.number_input("أعلى سعر",format="%.2f")
    l = c3.number_input("أقل سعر",format="%.2f")
    v = c4.number_input("عدد الأسهم")
    if p>0:
        show_report("MANUAL",p,h,l,v)

with tab3:
    st.subheader("📡 فرص مضاربية")
    res = scanner()
    if res:
        for r in res:
            st.error(r)
    else:
        st.success("لا توجد فرص حالياً")
