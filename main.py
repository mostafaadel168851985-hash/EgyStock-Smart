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
header, .main, .stApp { background-color: #0d1117 !important; }
h1,h2,h3,p,span,label,li { color: #ffffff !important; font-weight: bold; }

.stTabs [role="tab"] { background-color:#0d1117; color:white; font-weight:bold; }

.card {
    background: #161b22;
    color: #ffffff !important;
    padding: 22px;
    border-radius: 15px;
    border: 2px solid #3498db;
    margin-top: 15px;
}
.card * { color: #ffffff !important; }

.badge { padding:6px 12px; border-radius:12px; font-weight:bold; }
.up { background:#2ecc71; color:white; }
.down { background:#e74c3c; color:white; }
.flat { background:#f1c40f; color:black; }

.whatsapp-btn {
    background: linear-gradient(135deg, #25D366, #128C7E);
    padding: 12px;
    border-radius: 14px;
    text-align: center;
    color: white !important;
    font-size: 16px;
    font-weight: bold;
    display: block;
    margin-top: 18px;
}
</style>
""", unsafe_allow_html=True)

# ================== DATA ==================
@st.cache_data(ttl=600)
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
    piv = (p + h + l)/3
    s1 = (2*piv) - h
    s2 = piv - (h-l)
    r1 = (2*piv) - l
    r2 = piv + (h-l)
    return s1, s2, r1, r2

def trend_status(p, h, l):
    mid = (h+l)/2
    if p > mid*1.01:
        return "صاعد", "up"
    elif p < mid*0.99:
        return "هابط", "down"
    else:
        return "عرضي", "flat"

def rsi_fake(p,h,l):
    if h==l: return 50
    return ((p-l)/(h-l))*100

def liquidity(vol):
    if vol > 2_000_000: return "سيولة عالية"
    elif vol > 500_000: return "سيولة متوسطة"
    else: return "سيولة ضعيفة"

def ai_comment_trader(p,s1):
    return f"⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f}"

def ai_comment_swing():
    return "🔁 حركة تصحيح داخل اتجاه عام، راقب الارتداد"

def ai_comment_invest():
    return "🏦 اتجاه طويل الأجل إيجابي طالما السعر أعلى المتوسط"

def make_recommendation(p,s1,r1,rsi):
    rec = "انتظار"
    if p <= s1*1.02 and rsi<40: rec="شراء"
    elif p >= r1*0.98 and rsi>70: rec="بيع"
    return rec

# ================== REPORT ==================
def show_report(code,p,h,l,vol):
    company = COMPANIES.get(code,"")
    s1,s2,r1,r2 = pivots(p,h,l)
    trend, cls = trend_status(p,h,l)
    rsi = rsi_fake(p,h,l)
    liq = liquidity(vol)
    rec = make_recommendation(p,s1,r1,rsi)

    wa_msg = f"""
📊 تحليل {code} - {company}
💰 السعر: {p:.2f}
📈 الاتجاه: {trend}
⚡ RSI: {rsi:.1f}
💧 السيولة: {liq}
🏹 التوصية: {rec}
"""
    st.markdown(f"""
    <div class="card">
        <h3 style="text-align:center;">{code} – {company}</h3>
        <p>💰 السعر: {p:.2f}</p>
        <p>📈 الاتجاه: <span class="badge {cls}">{trend}</span></p>
        <p>⚡ RSI: {rsi:.1f}</p>
        <p>💧 السيولة: {liq}</p>
        <hr>
        <p><b>🎯 المضارب:</b> {ai_comment_trader(p,s1)}</p>
        <p><b>🔁 سوينج:</b> {ai_comment_swing()}</p>
        <p><b>🏦 المستثمر:</b> {ai_comment_invest()}</p>
        <hr>
        <p>🧱 الدعم: {s1:.2f} / {s2:.2f}</p>
        <p>🚧 المقاومة: {r1:.2f} / {r2:.2f}</p>
        <hr>
        <p><b>📌 التوصية:</b> {rec}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<a class="whatsapp-btn" href="https://wa.me/?text={urllib.parse.quote(wa_msg)}">📲 مشاركة التحليل على واتساب</a>',
        unsafe_allow_html=True
    )

# ================== SCANNER ==================
def scanner():
    results=[]
    for s in WATCHLIST:
        p,h,l,v = get_data(s)
        if p:
            s1,s2,r1,r2 = pivots(p,h,l)
            rsi = rsi_fake(p,h,l)
            rec = make_recommendation(p,s1,r1,rsi)
            if p <= s1*1.02 and rsi<40:
                results.append(f"🚨 {s} ({COMPANIES.get(s,'')}) | سعر {p:.2f} | دعم {s1:.2f} | هدف {r1:.2f} | توصية: {rec}")
    return results

# ================== UI ==================
st.title("🏹 EGX Sniper PRO")

tab1,tab2,tab3 = st.tabs(["📡 تحليل لحظي","🛠️ يدوي","🚨 Scanner"])

with tab1:
    code = st.text_input("ادخل كود السهم").upper().strip()
    if code:
        p,h,l,v = get_data(code)
        if p: show_report(code,p,h,l,v)
        else: st.error("فشل جلب البيانات")

with tab2:
    st.subheader("تحليل يدوي")
    p = st.number_input("السعر",format="%.2f")
    h = st.number_input("أعلى",format="%.2f")
    l = st.number_input("أقل",format="%.2f")
    v = st.number_input("عدد الأسهم")
    code_manual = st.text_input("كود السهم")
    if st.button("تحليل يدوي") and p>0:
        show_report(code_manual or "MANUAL",p,h,l,v)

with tab3:
    st.subheader("📡 فرص مضاربية")
    res=scanner()
    if res:
        for r in res: st.error(r)
    else: st.success("لا توجد فرص حالياً")
