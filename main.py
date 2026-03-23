import streamlit as st
import requests
import pandas as pd

# لازم يكون أول حاجة
st.set_page_config(page_title="EGX Sniper PRO", layout="wide")

st.title("🏹 EGX Sniper PRO")

# ================== STOCKS ==================
WATCHLIST = ["TMGH","COMI","ETEL","SWDY","EFID","ATQA","ALCN","RMDA"]
ALL_STOCKS = WATCHLIST + ["ORAS","FWRY","AMOC","HELI"]

# ================== DATA ==================
@st.cache_data(ttl=300)
def get_data(symbol):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "symbols":{"tickers":[f"EGX:{symbol}"],"query":{"types":[]}},
            "columns":["close","high","low","volume"]
        }
        r = requests.post(url,json=payload)
        data = r.json()

        if "data" not in data or len(data["data"]) == 0:
            return None,None,None,None

        d = data["data"][0]["d"]
        return float(d[0]),float(d[1]),float(d[2]),float(d[3])
    except:
        return None,None,None,None

# ================== CALC ==================
def pivots(p,h,l):
    piv=(p+h+l)/3
    s1=(2*piv)-h
    s2=piv-(h-l)
    r1=(2*piv)-l
    r2=piv+(h-l)
    return s1,s2,r1,r2

def rsi_fake(p,h,l):
    if h==l:
        return 50
    return ((p-l)/(h-l))*100

def liquidity(v):
    if v>2000000:
        return "سيولة عالية"
    elif v>500000:
        return "سيولة متوسطة"
    else:
        return "سيولة ضعيفة"

# ================== CARD ==================
def show_report(code,p,h,l,v):

    s1,s2,r1,r2 = pivots(p,h,l)
    rsi = rsi_fake(p,h,l)
    liq = liquidity(v)

    # Signals
    if p <= s1 * 1.02 and rsi < 30:
        signal = "🟢 إشارة ارتداد صاعد"
    else:
        signal = "↪️ لا توجد إشارة ارتداد"

    confirm = "⚪ لا يوجد تأكيد"

    trader_score = 50
    swing_score = round(60 + (50-abs(50-rsi)),2)
    investor_score = 55

    st.markdown(f"""
    <div style="
        background:#161b22;
        padding:25px;
        border-radius:15px;
        color:white;
        font-size:16px;
        line-height:1.8;
    ">

    <h3>{code}</h3>

    💰 السعر الحالي: {p:.2f}<br>
    📉 RSI: {rsi:.1f}<br>

    🧱 الدعم: {s1:.2f} / {s2:.2f}<br>
    🚧 المقاومة: {r1:.2f} / {r2:.2f}<br>
    💧 السيولة: {liq}<br>

    <hr>

    🔄 {signal}<br>
    ⚡ {confirm}<br>

    <hr>

    🎯 المضارب: {trader_score}/100<br>
    دخول: {round(s1+0.1,2)} | وقف خسارة: {round(s1-0.15,2)}<br><br>

    🔁 السوينج: {swing_score}/100<br>
    دخول: {round((s1+r1)/2,2)} | وقف خسارة: {round((s1+r1)/2-0.25,2)}<br><br>

    🏦 المستثمر: {investor_score}/100<br>
    دخول: {round((s1+s2)/2,2)} | وقف خسارة: {round(s2-0.25,2)}<br>

    <hr>

    📌 التوصية: <b>انتظار</b><br>

    📝 ملحوظة للمحبوس:<br>
    أقرب دعم {s1:.2f} - دعم أقوى {s2:.2f}

    </div>
    """, unsafe_allow_html=True)

# ================== SCANNER ==================
def scanner():
    rows = []

    for s in ALL_STOCKS:
        p,h,l,v = get_data(s)

        if p is None:
            continue

        s1,s2,r1,r2 = pivots(p,h,l)
        rsi = rsi_fake(p,h,l)
        liq = liquidity(v)

        dist = abs(p-s1)/p*100

        if dist < 1:
            signal="🔥 لاصق دعم"
        elif dist < 2:
            signal="🟢 قريب دعم"
        else:
            signal="⚪ بعيد"

        rows.append({
            "السهم":s,
            "السعر":round(p,2),
            "RSI":round(rsi,1),
            "الدعم":round(s1,2),
            "المقاومة":round(r1,2),
            "السيولة":liq,
            "الحالة":signal
        })

    if len(rows) == 0:
        return pd.DataFrame()

    return pd.DataFrame(rows)

# ================== UI ==================
tab1,tab2,tab3 = st.tabs(["📊 تحليل سهم","🛠️ يدوي","🚨 Scanner"])

# تحليل
with tab1:
    code = st.text_input("ادخل كود السهم").upper()
    if code:
        p,h,l,v = get_data(code)
        if p:
            show_report(code,p,h,l,v)
        else:
            st.warning("السهم غير متاح")

# يدوي
with tab2:
    p = st.number_input("السعر",0.0)
    h = st.number_input("أعلى",0.0)
    l = st.number_input("أقل",0.0)
    v = st.number_input("السيولة",0.0)

    if p>0:
        show_report("MANUAL",p,h,l,v)

# Scanner
with tab3:
    df = scanner()

    if df.empty:
        st.warning("لا توجد بيانات حالياً")
    else:
        st.dataframe(df,use_container_width=True)
