import streamlit as st
import requests
import urllib.parse

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
body, .stApp, .main {background-color: #0d1117; color: #ffffff;}
h1,h2,h3,p,label,span {color: #ffffff;}
.stTabs button {background-color: #0d1117 !important; color: #ffffff !important;}
.stTabs button:hover {background-color: #161b22 !important;}
.card {background-color:#161b22; color:white; padding:20px; border-radius:15px; margin-bottom:20px;}
.score {font-size:22px; font-weight:bold; color:#00ff99;}
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
.warning {color:#f39c12; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.title("🏹 EGX Sniper PRO - Dark Mode")

# ================== FUNCTIONS ==================
def get_data(symbol):
    """جلب بيانات لحظية تقريبية من TradingView API"""
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

def pivots(p, h, l):
    piv = (p + h + l)/3
    s1 = (2*piv) - h
    s2 = piv - (h - l)
    r1 = (2*piv) - l
    r2 = piv + (h - l)
    return s1, s2, r1, r2

def trend_status(p, h, l):
    mid = (h + l)/2
    if p > mid*1.01:
        return "صاعد"
    elif p < mid*0.99:
        return "هابط"
    else:
        return "عرضي"

def rsi_fake(p, h, l):
    if h==l: return 50
    return ((p-l)/(h-l))*100

def liquidity(vol):
    if vol > 2_000_000: return "سيولة عالية"
    elif vol > 500_000: return "سيولة متوسطة"
    else: return "سيولة ضعيفة"

def make_recommendation(p, s1, r1, trend, rsi):
    rec = "انتظار"
    reasons = []
    if p <= s1*1.02 and rsi<40:
        rec = "شراء"
        reasons += ["قرب من دعم قوي","RSI منخفض"]
    elif p >= r1*0.98 and rsi>70:
        rec = "بيع"
        reasons += ["قرب من مقاومة","RSI مرتفع"]
    else:
        reasons += ["لا توجد إشارة مكتملة"]
    reasons.append(f"الاتجاه العام: {trend}")
    return rec, reasons

def ai_comment_trader(p, s1): return f"⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f}"
def ai_comment_swing(): return "🔁 حركة تصحيح، راقب الارتداد"
def ai_comment_invest(): return "🏦 الاتجاه طويل الأجل إيجابي طالما السعر أعلى المتوسط"

def show_report(code, p, h, l, vol):
    company = COMPANIES.get(code,"")
    s1,s2,r1,r2 = pivots(p,h,l)
    trend = trend_status(p,h,l)
    rsi = rsi_fake(p,h,l)
    liq = liquidity(vol)
    rec, reasons = make_recommendation(p,s1,r1,trend,rsi)

    trader_score = min(100, 50 + (20 if rsi<30 else 0) + (15 if abs(p-s1)/s1<0.02 else 0))
    swing_score = min(100, 60 + (50 - abs(50 - rsi)))
    invest_score = 80 if p > (h+l)/2 else 55

    # ===== CARD =====
    st.markdown(f"""
    <div class="card">
    <h3>{code} – {company}</h3>
    💰 السعر: {p:.2f}<br>
    🧱 الدعم: {s1:.2f} / {s2:.2f}<br>
    🚧 المقاومة: {r1:.2f} / {r2:.2f}<br>
    ⚡ RSI: {rsi:.1f}<br>
    💧 السيولة: {liq}<br><br>
    🎯 <b>مضارب:</b> {trader_score}/100 | {ai_comment_trader(p,s1)}<br>
    🔁 <b>سوينج:</b> {swing_score}/100 | {ai_comment_swing()}<br>
    🏦 <b>مستثمر:</b> {invest_score}/100 | {ai_comment_invest()}<br>
    <b>التوصية:</b> {rec}
    </div>
    """, unsafe_allow_html=True)

    # WhatsApp
    wa_msg = f"""
📊 تحليل {code} - {company}
💰 السعر: {p:.2f}
🧱 الدعم: {s1:.2f} / {s2:.2f}
🚧 المقاومة: {r1:.2f} / {r2:.2f}
⚡ RSI: {rsi:.1f}
💧 السيولة: {liq}
🎯 مضارب: {trader_score}/100
🔁 سوينج: {swing_score}/100
🏦 مستثمر: {invest_score}/100
📌 التوصية: {rec}
"""
    wa_url = "https://wa.me/?text=" + urllib.parse.quote(wa_msg)
    st.markdown(f'<a href="{wa_url}" class="whatsapp-btn" target="_blank">📲 مشاركة التحليل على واتساب</a>', unsafe_allow_html=True)

def scanner():
    alerts = []
    for s in WATCHLIST:
        p,h,l,v = get_data(s)
        if p:
            s1, s2, r1, r2 = pivots(p,h,l)
            rsi = rsi_fake(p,h,l)
            if p<=s1*1.02 and rsi<40:
                alerts.append(f"🚨 {s} ({COMPANIES.get(s,'')}) | سعر {p:.2f} | دعم {s1:.2f} | هدف {r1:.2f} | RSI {rsi:.1f}")
    return alerts

# ================== UI ==================
tab1,tab2,tab3 = st.tabs(["📡 تحليل آلي","🛠️ يدوي","🚨 Scanner"])

with tab1:
    code = st.text_input("ادخل كود السهم").upper().strip()
    if code:
        p,h,l,v = get_data(code)
        if p: show_report(code,p,h,l,v)
        else: st.error("⚠️ البيانات للسهم غير متاحة، استخدم التحليل اليدوي")

with tab2:
    c1,c2,c3,c4 = st.columns(4)
    p = c1.number_input("السعر",format="%.2f")
    h = c2.number_input("أعلى",format="%.2f")
    l = c3.number_input("أقل",format="%.2f")
    v = c4.number_input("عدد الأسهم")
    if p>0: show_report("MANUAL",p,h,l,v)

with tab3:
    st.subheader("📡 فرص مضاربية قريبة من الدعم")
    res = scanner()
    if res:
        for r in res: st.error(r)
    else: st.success("لا توجد فرص حالياً")
