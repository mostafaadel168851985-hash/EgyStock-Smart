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
/* Dark background كامل */
header, .main, .stApp { background-color: #0d1117 !important; color:white !important; }

/* Tabs style */
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

/* Card style */
.card {
    background:#161b22;
    color:white !important;
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
    border: 1px solid #444;
}
.score {font-size:24px; font-weight:bold; color:#00ff99;}
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
@st.cache_data(ttl=10)
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
    s1 = (2*piv - h)
    s2 = piv - (h - l)
    r1 = (2*piv - l)
    r2 = piv + (h - l)
    return s1, s2, r1, r2

def trend_status(p,h,l):
    mid = (h+l)/2
    if p > mid*1.01:
        return "صاعد", "up"
    elif p < mid*0.99:
        return "هابط", "down"
    else:
        return "عرضي", "flat"

def rsi_fake(p,h,l):
    return ((p-l)/(h-l)*100) if h!=l else 50

def liquidity(vol):
    if vol > 2_000_000:
        return "سيولة عالية"
    elif vol > 500_000:
        return "سيولة متوسطة"
    else:
        return "سيولة ضعيفة"

# ================== SCORE + AI ==================
def score_trader(rsi_val, price, s1):
    score = 50
    if rsi_val < 30: score += 20
    if abs(price - s1)/s1 < 0.02: score += 15
    return min(score,100)

def score_swing(rsi_val):
    return min(100, 60 + (50 - abs(50 - rsi_val)))

def score_invest(price, s2):
    return 80 if price > s2 else 55

def ai_comment_trader(price, s1):
    return f"⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f} مع الالتزام بوقف الخسارة."

def ai_comment_swing():
    return "🔁 حركة تصحيح داخل اتجاه عام، مراقبة الارتداد مطلوبة."

def ai_comment_invest():
    return "🏦 الاتجاه طويل الأجل إيجابي طالما السعر أعلى المتوسط."

# ================== REPORT ==================
def show_report(code, p, h, l, vol):
    company = COMPANIES.get(code,"")
    s1,s2,r1,r2 = pivots(p,h,l)
    trend, cls = trend_status(p,h,l)
    rsi = rsi_fake(p,h,l)
    liq = liquidity(vol)

    trader_score = score_trader(rsi,p,s1)
    swing_score = score_swing(rsi)
    invest_score = score_invest(p,s2)

    st.markdown(f"""
    <div class="card">
    <h3>{code} - {company}</h3>
    💰 السعر الحالي: {p:.2f}<br>
    📈 الاتجاه: {trend}<br>
    ⚡ RSI: {rsi:.1f}<br>
    🧱 الدعم: {s1:.2f} / {s2:.2f}<br>
    🚧 المقاومة: {r1:.2f} / {r2:.2f}<br>
    💧 السيولة: {liq}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
    🎯 <b>مضارب</b><br>
    <span class="score">{trader_score}/100</span><br>
    {ai_comment_trader(p,s1)}
    </div>
    <div class="card">
    🔁 <b>سوينج</b><br>
    <span class="score">{swing_score}/100</span><br>
    {ai_comment_swing()}
    </div>
    <div class="card">
    🏦 <b>مستثمر</b><br>
    <span class="score">{invest_score}/100</span><br>
    {ai_comment_invest()}
    </div>
    """, unsafe_allow_html=True)

    # WhatsApp
    wa_msg = f"""
📊 تحليل {code} - {company}
💰 السعر: {p:.2f}
📈 الاتجاه: {trend}
⚡ RSI: {rsi:.1f}
🧱 الدعم: {s1:.2f} / {s2:.2f}
🚧 المقاومة: {r1:.2f} / {r2:.2f}
💧 السيولة: {liq}

🎯 مضارب: {trader_score}/100
🔁 سوينج: {swing_score}/100
🏦 مستثمر: {invest_score}/100
"""
    wa_url = "https://wa.me/?text=" + urllib.parse.quote(wa_msg)
    st.markdown(f'<a href="{wa_url}" class="whatsapp-btn" target="_blank">📲 مشاركة التحليل على واتساب</a>', unsafe_allow_html=True)

# ================== SCANNER ==================
def scanner():
    results = []
    for s in WATCHLIST:
        p,h,l,v = get_data(s)
        if p:
            s1,_,r1,_ = pivots(p,h,l)
            rsi = rsi_fake(p,h,l)
            if p <= s1*1.02 and rsi < 40:
                results.append(f"🚨 {s} ({COMPANIES.get(s,'')}) | سعر {p:.2f} | دعم {s1:.2f} | هدف {r1:.2f}")
    return results

# ================== UI ==================
st.title("🏹 EGX Sniper PRO - Dark Mode")

tab1,tab2,tab3 = st.tabs(["📡 التحليل الآلي","🛠️ التحليل اليدوي","🚨 Scanner"])

with tab1:
    code = st.text_input("ادخل كود السهم").upper().strip()
    refresh = st.slider("تحديث (ثواني)",5,60,15)
    if code:
        p,h,l,v = get_data(code)
        if p:
            show_report(code,p,h,l,v)
        else:
            st.warning("⚠️ البيانات غير متاحة، استخدم التحليل اليدوي")

        time.sleep(refresh)
        st.experimental_rerun()

with tab2:
    code_manual = st.text_input("كود السهم يدويًا").upper().strip()
    open_price = st.number_input("سعر الافتتاح اليوم",format="%.2f")
    high_price = st.number_input("أعلى سعر اليوم",format="%.2f")
    low_price = st.number_input("أقل سعر اليوم",format="%.2f")
    volume = st.number_input("عدد الأسهم المتداولة اليوم",value=0)
    if st.button("تحليل يدوي"):
        if volume>0:
            liq_today = volume * open_price
        else: liq_today=0
        show_report(code_manual,open_price,high_price,low_price,volume)

with tab3:
    st.subheader("🚨 فرص مضاربية قرب الدعم")
    alerts = scanner()
    if alerts:
        for a in alerts:
            st.error(a)
    else:
        st.success("لا توجد فرص حالياً")
