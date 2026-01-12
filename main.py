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
/* Dark background */
body, .stApp, .main { background-color:#0d1117; color:#ffffff; }
/* Main title */
h1, h2, h3, p, span, label { color:#ffffff !important; font-weight:bold; }
/* Tabs always dark with white text */
.css-1d391kg { background-color:#161b22 !important; color:#ffffff !important; }
/* Card */
.card { background:#161b22; color:#ffffff; padding:20px; border-radius:15px; margin-bottom:15px; border:1px solid #3498db;}
.card * { color:#ffffff !important; }
/* Badges */
.badge { padding:6px 14px; border-radius:14px; font-weight:bold;}
.up { background:#2ecc71; color:white; }
.down { background:#e74c3c; color:white; }
.flat { background:#f1c40f; color:black; }
/* WhatsApp button */
.whatsapp-btn { background: linear-gradient(135deg,#25D366,#128C7E); padding:12px; border-radius:14px; text-align:center; color:white !important; font-weight:bold; text-decoration:none; display:block; margin-top:12px;}
</style>
""", unsafe_allow_html=True)

# ================== DATA ==================
@st.cache_data(ttl=600)
def get_data(symbol):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "symbols": {"tickers":[f"EGX:{symbol}"],"query":{"types":[]}},
            "columns":["close","high","low","volume"]
        }
        r = requests.post(url,json=payload,timeout=10).json()
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

def trend_status(p,h,l):
    mid = (h+l)/2
    if p > mid*1.01: return "صاعد","up"
    elif p < mid*0.99: return "هابط","down"
    else: return "عرضي","flat"

def rsi_fake(p,h,l):
    if h==l: return 50
    return ((p-l)/(h-l))*100

def liquidity(vol):
    if vol>2_000_000: return "سيولة عالية"
    elif vol>500_000: return "سيولة متوسطة"
    else: return "سيولة ضعيفة"

# ================== AI COMMENTS ==================
def ai_trader(p,s1):
    return f"⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f}"

def ai_swing():
    return "🔁 حركة تصحيح داخل الاتجاه العام، راقب الارتداد"

def ai_invest():
    return "🏦 الاتجاه طويل الأجل إيجابي طالما السعر أعلى المتوسط 50 يوم"

# ================== RECOMMENDATION ==================
def make_recommendation(p,s1,r1,trend,rsi):
    reasons = []
    rec = "انتظار"
    if p <= s1*1.02 and rsi < 40:
        rec="شراء"
        reasons += ["قرب من دعم قوي","RSI منخفض"]
    elif p >= r1*0.98 and rsi > 70:
        rec="بيع"
        reasons += ["قرب من مقاومة","RSI مرتفع"]
    else:
        reasons.append("لا توجد إشارة مكتملة")
    reasons.append(f"الاتجاه العام: {trend}")
    return rec,reasons

# ================== REPORT ==================
def show_report(code,p,h,l,vol):
    company = COMPANIES.get(code,"")
    s1,s2,r1,r2 = pivots(p,h,l)
    trend,cls = trend_status(p,h,l)
    rsi = rsi_fake(p,h,l)
    liq = liquidity(vol)
    rec,reasons = make_recommendation(p,s1,r1,trend,rsi)

    wa_msg = f"""
تحليل {code} - {company}
السعر: {p:.2f}
الاتجاه: {trend}
RSI: {rsi:.1f}
السيولة: {liq}

المضارب: {ai_trader(p,s1)}
سوينج: {ai_swing()}
مستثمر: {ai_invest()}

التوصية: {rec}
"""

    st.markdown(f"""
    <div class="card">
        <h3 style="text-align:center;">📊 {code} – {company}</h3>
        <p>💰 السعر: {p:.2f}</p>
        <p>📈 الاتجاه: <span class="badge {cls}">{trend}</span></p>
        <p>⚡ RSI: {rsi:.1f}</p>
        <p>💧 السيولة: {liq}</p>
        <hr>
        <p><b>🎯 المضارب:</b> {ai_trader(p,s1)}</p>
        <p><b>🔁 سوينج:</b> {ai_swing()}</p>
        <p><b>🏦 مستثمر:</b> {ai_invest()}</p>
        <hr>
        <p><b>📌 التوصية:</b> {rec}</p>
        <ul>{"".join(f"<li>{r}</li>" for r in reasons)}</ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<a class="whatsapp-btn" href="https://wa.me/?text={urllib.parse.quote(wa_msg)}">📲 مشاركة التحليل على واتساب</a>',unsafe_allow_html=True)

# ================== SCANNER ==================
def scanner():
    results=[]
    for s in WATCHLIST:
        p,h,l,v = get_data(s)
        if p:
            s1,s2,r1,r2 = pivots(p,h,l)
            rsi=rsi_fake(p,h,l)
            if p <= s1*1.02 and rsi <40:
                results.append(f"🚨 {s} ({COMPANIES.get(s,'')}) | سعر {p:.2f} | دعم {s1:.2f}/{s2:.2f} | مقاومة {r1:.2f}/{r2:.2f}")
    return results

# ================== UI ==================
st.title("🏹 EGX Sniper PRO")

tab1,tab2,tab3 = st.tabs(["📡 تحليل لحظي","🛠️ يدوي","🚨 Scanner"])

# ===== TAB 1 =====
with tab1:
    code = st.text_input("ادخل كود السهم").upper().strip()
    if code:
        p,h,l,v = get_data(code)
        if p:
            show_report(code,p,h,l,v)
        else:
            st.error("فشل جلب البيانات")

# ===== TAB 2 =====
with tab2:
    c1,c2,c3,c4 = st.columns(4)
    p = c1.number_input("السعر",format="%.2f")
    h = c2.number_input("أعلى",format="%.2f")
    l = c3.number_input("أقل",format="%.2f")
    v = c4.number_input("السيولة")
    if p>0:
        show_report("MANUAL",p,h,l,v)

# ===== TAB 3 =====
with tab3:
    st.subheader("📡 فرص مضاربية قريبة من الدعم")
    res = scanner()
    if res:
        for r in res: st.error(r)
    else:
        st.success("لا توجد فرص حالياً")
