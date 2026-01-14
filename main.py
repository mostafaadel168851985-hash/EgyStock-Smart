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
body, .stApp, .main {background-color: #0d1117; color: #ffffff;}
h1,h2,h3,p,label,span {color: #ffffff; font-weight:bold;}
.stTabs button {background-color:#161b22; color:white; font-weight:bold;}
.stTabs [data-baseweb="tab-list"] button {color:white;}
.card {background-color:#161b22; padding:20px; border-radius:15px; margin-bottom:20px; color:white;}
.score {font-size:26px; font-weight:bold; color:#00ff99;}
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
.up {color:#2ecc71;}
.down {color:#e74c3c;}
.flat {color:#f1c40f;}
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

# ================== AI COMMENTS ==================
def ai_comment_trader(p, s1):
    return f"⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f} مع الالتزام بوقف الخسارة."

def ai_comment_swing():
    return "🔁 السهم في حركة تصحيح داخل اتجاه عام، مراقبة الارتداد مطلوبة."

def ai_comment_invest():
    return "🏦 الاتجاه طويل الأجل إيجابي طالما السعر أعلى المتوسط 50 يوم."

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
    else:
        reasons.append("لا توجد إشارة مكتملة")
    reasons.append(f"الاتجاه العام: {trend}")
    return rec, reasons

# ================== REPORT ==================
def show_report(code, p, h, l, v):
    company = COMPANIES.get(code, "")
    s1, s2, r1, r2 = pivots(p, h, l)
    trend, cls = trend_status(p, h, l)
    rsi = rsi_fake(p, h, l)
    liq = liquidity(v)
    rec, reasons = make_recommendation(p, s1, r1, trend, rsi)

    trader_score = min(100, 50 + (20 if rsi < 30 else 0) + (15 if abs(p - s1)/s1 < 0.02 else 0))
    swing_score = min(100, 60 + (50 - abs(50 - rsi)))
    invest_score = 80 if p > (h+l)/2 else 55

    st.markdown(f"""
    <div class="card">
    <h3>{code} - {company}</h3>
    💰 السعر الحالي: {p:.2f}<br>
    📉 RSI: {rsi:.1f} ({'شراء' if rsi<30 else 'بيع' if rsi>70 else 'انتظار'})<br>
    🧱 الدعم: {s1:.2f} / {s2:.2f}<br>
    🚧 المقاومة: {r1:.2f} / {r2:.2f}<br>
    💧 السيولة: {liq}<br>
    <hr>
    🎯 <b>مضارب</b>: {trader_score}/100<br>
    {ai_comment_trader(p,s1)}<br><br>
    🔁 <b>سوينج</b>: {swing_score}/100<br>
    {ai_comment_swing()}<br><br>
    🏦 <b>مستثمر</b>: {invest_score}/100<br>
    {ai_comment_invest()}<br>
    <hr>
    📌 التوصية: {rec}<br>
    <b>⚠️ إشارة ارتداد / تأكيد:</b> {"ارتداد صعود" if rec=="شراء" else "ارتداد هبوط" if rec=="بيع" else "لا يوجد"}<br>
    </div>
    """, unsafe_allow_html=True)

    whatsapp_msg = f"""
📊 تحليل سهم {code} - {company}
💰 السعر: {p:.2f}
📉 RSI: {rsi:.1f} ({'شراء' if rsi<30 else 'بيع' if rsi>70 else 'انتظار'})
🧱 الدعم: {s1:.2f} / {s2:.2f}
🚧 المقاومة: {r1:.2f} / {r2:.2f}
💧 السيولة: {liq}

🎯 مضارب: {trader_score}/100
🔁 سوينج: {swing_score}/100
🏦 مستثمر: {invest_score}/100

📌 التوصية: {rec}
⚠️ إشارة ارتداد / تأكيد: {"ارتداد صعود" if rec=="شراء" else "ارتداد هبوط" if rec=="بيع" else "لا يوجد"}
"""
    wa_url = "https://wa.me/?text=" + urllib.parse.quote(whatsapp_msg)
    st.markdown(f'<a href="{wa_url}" class="whatsapp-btn" target="_blank">📲 مشاركة التحليل على واتساب</a>', unsafe_allow_html=True)

# ================== SCANNER ==================
def scanner():
    results = []
    for s in WATCHLIST:
        p,h,l,v = get_data(s)
        if p:
            s1,s2,r1,r2 = pivots(p,h,l)
            rsi = rsi_fake(p,h,l)
            rec,_ = make_recommendation(p,s1,r1,*trend_status(p,h,l),rsi)
            results.append(f"🚨 {s} ({COMPANIES.get(s,'')}) | سعر: {p:.2f} | دعم: {s1:.2f}/{s2:.2f} | مقاومة: {r1:.2f}/{r2:.2f} | RSI: {rsi:.1f} | توصية: {rec}")
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
            st.error("⚠️ البيانات للسهم غير متاحة، استخدم التحليل اليدوي")

with tab2:
    st.subheader("🛠️ التحليل اليدوي")
    p = st.number_input("سعر الإفتتاح اليوم", format="%.2f")
    h = st.number_input("أعلى سعر اليوم", format="%.2f")
    l = st.number_input("أقل سعر اليوم", format="%.2f")
    v = st.number_input("عدد الأسهم المتداولة", value=0)
    if p>0:
        show_report("MANUAL",p,h,l,v)

with tab3:
    st.subheader("🚨 فرص مضاربية قرب الدعم")
    res = scanner()
    if res:
        for r in res:
            st.success(r)
    else:
        st.info("لا توجد فرص حالياً")
