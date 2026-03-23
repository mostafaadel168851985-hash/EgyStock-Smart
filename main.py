import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="EGX Sniper PRO", layout="wide")

# ====== STOCKS ======
WATCHLIST = ["TMGH","COMI","ETEL","SWDY","EFID","ATQA","ALCN","RMDA"]
ALL_STOCKS = WATCHLIST + ["ORAS","FWRY","AMOC","HELI","PHDC","MNHD","EKHO"]

COMPANIES = {
    "TMGH": "طلعت مصطفى",
    "COMI": "البنك التجاري الدولي",
    "ETEL": "المصرية للاتصالات",
    "SWDY": "السويدي",
    "EFID": "إيديتا",
    "ATQA": "عتاقة",
    "ALCN": "ألكون",
    "RMDA": "رمادا"
}

# ====== STYLE ======
st.markdown("""
<style>
body, .stApp {
    background-color:#0d1117;
    color:white;
}
.card {
    background:#161b22;
    padding:25px;
    border-radius:15px;
    font-size:17px;
    line-height:1.8;
}
h2 {color:white;}
</style>
""", unsafe_allow_html=True)

# ====== DATA ======
@st.cache_data(ttl=300)
def get_data(symbol):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "symbols":{"tickers":[f"EGX:{symbol}"],"query":{"types":[]}},
            "columns":["close","high","low","volume"]
        }
        r = requests.post(url,json=payload).json()
        d = r["data"][0]["d"]
        return float(d[0]),float(d[1]),float(d[2]),float(d[3])
    except:
        return None,None,None,None

# ====== CALC ======
def pivots(p,h,l):
    piv=(p+h+l)/3
    s1=(2*piv)-h
    s2=piv-(h-l)
    r1=(2*piv)-l
    r2=piv+(h-l)
    return s1,s2,r1,r2

def rsi_fake(p,h,l):
    if h==l: return 50
    return ((p-l)/(h-l))*100

def liquidity(v):
    if v>2000000: return "سيولة عالية"
    elif v>500000: return "سيولة متوسطة"
    else: return "سيولة ضعيفة"

# ====== AI ======
def ai_block(p,s1,s2,r1,r2,rsi):
    trader = min(100,50+(20 if rsi<30 else 0))
    swing = min(100,60+(50-abs(50-rsi)))
    investor = 80 if p>s1 else 55

    return trader,swing,investor

# ====== REPORT ======
def show_report(code,p,h,l,v):
    s1,s2,r1,r2 = pivots(p,h,l)
    rsi = rsi_fake(p,h,l)
    liq = liquidity(v)

    t,s,i = ai_block(p,s1,s2,r1,r2,rsi)

    st.markdown(f"""
    <div class="card">

    <h2>{code} - {COMPANIES.get(code,'')}</h2>

    💰 السعر: {p:.2f}  
    📉 RSI: {rsi:.1f}  

    🧱 الدعم: {s1:.2f} / {s2:.2f}  
    🚧 المقاومة: {r1:.2f} / {r2:.2f}  
    💧 السيولة: {liq}  

    ---------------------

    🎯 المضارب: {t}/100  
    دخول: {round(s1+0.1,2)} | وقف: {round(s1-0.15,2)}  

    🔁 السوينج: {s}/100  
    دخول: {round((s1+r1)/2,2)} | وقف: {round((s1+r1)/2-0.25,2)}  

    🏦 المستثمر: {i}/100  
    دخول: {round((s1+s2)/2,2)} | وقف: {round(s2-0.25,2)}  

    ---------------------

    📌 التوصية: انتظار  

    📝 المحبوس: أقرب دعم {s1:.2f} ثم {s2:.2f}

    </div>
    """, unsafe_allow_html=True)

# ====== SCANNER ======
def scanner():
    rows=[]
    for s in ALL_STOCKS:
        p,h,l,v = get_data(s)
        if not p: continue

        s1,s2,r1,r2 = pivots(p,h,l)
        rsi = rsi_fake(p,h,l)
        liq = liquidity(v)

        dist = abs(p-s1)/p*100

        if dist<1:
            signal="🔥 لاصق"
        elif dist<2:
            signal="🟢 قريب"
        else:
            signal="⚪ بعيد"

        rows.append({
            "السهم":s,
            "السعر":round(p,2),
            "RSI":round(rsi,1),
            "الدعم":round(s1,2),
            "المقاومة":round(r1,2),
            "السيولة":liq,
            "وضع الدعم":signal
        })

    return pd.DataFrame(rows)

# ====== UI ======
st.title("🏹 EGX Sniper PRO")

tab1,tab2,tab3 = st.tabs(["تحليل سهم","يدوي","Scanner"])

# ===== AUTO =====
with tab1:
    code = st.text_input("ادخل كود السهم").upper()
    if code:
        p,h,l,v = get_data(code)
        if p:
            show_report(code,p,h,l,v)

# ===== MANUAL =====
with tab2:
    p = st.number_input("السعر")
    h = st.number_input("أعلى سعر")
    l = st.number_input("أقل سعر")
    v = st.number_input("السيولة")

    if p>0:
        show_report("MANUAL",p,h,l,v)

# ===== SCANNER =====
with tab3:
    df = scanner()

    opt = st.radio("فلتر:",["الكل","سوينج","مضاربة"])

    if opt=="سوينج":
        df = df[(df["RSI"]>=40)&(df["RSI"]<=65)]
    elif opt=="مضاربة":
        df = df[(df["RSI"]>70)]

    st.dataframe(df,use_container_width=True)
