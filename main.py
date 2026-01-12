import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import urllib.parse
import time

# =====================
# CONFIGURATION
# =====================
st.set_page_config(page_title="EGX Sniper PRO", layout="wide")

WATCHLIST = ["TMGH.CA", "COMI.CA", "ETEL.CA", "SWDY.CA", "EFID.CA"]
COMPANIES = {
    "TMGH.CA": "طلعت مصطفى",
    "COMI.CA": "البنك التجاري الدولي",
    "ETEL.CA": "المصرية للاتصالات",
    "SWDY.CA": "السويدي إليكتريك",
    "EFID.CA": "إيديتا"
}

# =====================
# STYLING - Dark Mode كامل
# =====================
st.markdown("""
<style>
body, .stApp, .main {background-color: #0d1117; color: #ffffff;}
h1, h2, h3, p, label, span {color: #ffffff;}
.card {background-color:#161b22; padding:20px; border-radius:15px; margin-bottom:20px;}
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
.warning {color:#f39c12; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# =====================
# FUNCTIONS
# =====================
def load_data(symbol):
    if not symbol.endswith(".CA"):
        symbol = symbol.upper() + ".CA"
    try:
        df = yf.download(symbol, period="6mo", interval="1d")
        df.dropna(inplace=True)
        return df
    except:
        return None

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def support_resistance(df):
    s1 = df['Low'].tail(15).min()
    s2 = df['Low'].tail(40).min()
    r1 = df['High'].tail(15).max()
    r2 = df['High'].tail(40).max()
    return s1, s2, r1, r2

def liquidity(df):
    df['Value'] = df['Close'] * df['Volume']
    today = int(df['Value'].iloc[-1])
    avg = int(df['Value'].rolling(20).mean().iloc[-1])
    return today, avg

def score_trader(rsi_val, price, support):
    if pd.isna(rsi_val) or pd.isna(price) or pd.isna(support):
        return 50
    score = 50
    if rsi_val < 30: score += 20
    if abs(price - support)/support < 0.02: score += 15
    return min(score, 100)

def score_swing(rsi_val):
    if pd.isna(rsi_val): return 60
    return min(100, 60 + (50 - abs(50 - rsi_val)))

def score_invest(df):
    if df.empty: return 60
    ma50 = df['Close'].rolling(50).mean().iloc[-1]
    price = df['Close'].iloc[-1]
    return 80 if price > ma50 else 55

def ai_comment_trader(price, s1):
    return f"⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f} مع الالتزام بوقف الخسارة."

def ai_comment_swing():
    return "🔁 السهم في حركة تصحيح داخل اتجاه عام، مراقبة الارتداد مطلوبة."

def ai_comment_invest():
    return "🏦 الاتجاه طويل الأجل إيجابي طالما السعر أعلى المتوسط 50 يوم."

def scanner_watchlist():
    alerts = []
    for symbol in WATCHLIST:
        df = load_data(symbol)
        if df is None or df.empty:
            continue
        try:
            price = df['Close'].iloc[-1]
            rsi_val = rsi(df['Close']).iloc[-1]
            s1, s2, r1, r2 = support_resistance(df)
            if price <= s1*1.02 and rsi_val < 40:
                alerts.append(f"🚨 {symbol} ({COMPANIES.get(symbol,'')}) | السعر: {price:.2f} | دعم: {s1:.2f} | هدف: {r1:.2f}")
        except:
            continue
    return alerts

# =====================
# UI
# =====================
st.title("🏹 EGX Sniper PRO - Dark Mode")

tab1, tab2, tab3 = st.tabs(["📡 التحليل الآلي", "🛠️ التحليل اليدوي", "🚨 Scanner"])

# TAB 1: التحليل الآلي
with tab1:
    symbol = st.text_input("🧾 كود السهم (مثال: TMGH)", "").upper().strip()
    refresh = st.slider("تحديث تلقائي (ثواني)", 5, 60, 15)

    if symbol:
        df = load_data(symbol)
        if df is None or df.empty:
            st.warning("⚠️ البيانات للسهم غير متاحة، استخدم التحليل اليدوي")
        else:
            price = df['Close'].iloc[-1]
            rsi_val = rsi(df['Close']).iloc[-1]
            s1, s2, r1, r2 = support_resistance(df)
            liq_today, liq_avg = liquidity(df)
            company_name = COMPANIES.get(symbol.upper() + ".CA", "")

            trader_score = score_trader(rsi_val, price, s1)
            swing_score = score_swing(rsi_val)
            invest_score = score_invest(df)

            st.markdown(f"""
            <div class="card">
            <h3>{symbol.upper()} - {company_name}</h3>
            💰 السعر الحالي: {price:.2f}<br>
            📉 RSI: {rsi_val:.1f}<br><br>
            🧱 الدعم: {s1:.2f} / {s2:.2f}<br>
            🚧 المقاومة: {r1:.2f} / {r2:.2f}<br><br>
            💧 السيولة اليوم: {liq_today:,} جنيه<br>
            📊 متوسط 20 يوم: {liq_avg:,} جنيه
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
            🎯 <b>مضارب</b><br>
            <span class="score">{trader_score}/100</span><br>
            {ai_comment_trader(price,s1)}
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

            whatsapp_msg = f"""
📊 *تحليل سهم {symbol.upper()} - {company_name}*

💰 السعر: {price:.2f}
📉 RSI: {rsi_val:.1f}
🧱 الدعم: {s1:.2f} / {s2:.2f}
🚧 المقاومة: {r1:.2f} / {r2:.2f}
💧 السيولة اليوم: {liq_today:,} جنيه
📊 متوسط 20 يوم: {liq_avg:,} جنيه

🎯 مضارب: {trader_score}/100
🔁 سوينج: {swing_score}/100
🏦 مستثمر: {invest_score}/100

⚠️ تحليل فني – قرارك مسؤوليتك 😁
"""
            wa_url = "https://wa.me/?text=" + urllib.parse.quote(whatsapp_msg)
            st.markdown(f'<a href="{wa_url}" class="whatsapp-btn" target="_blank">📲 مشاركة التحليل على واتساب</a>', unsafe_allow_html=True)

# TAB 2: التحليل اليدوي
with tab2:
    st.subheader("🛠️ التحليل اليدوي لأي سهم")
    symbol_manual = st.text_input("كود السهم يدويًا", "").upper().strip()
    open_price = st.number_input("سعر الافتتاح اليوم", format="%.2f")
    high_price = st.number_input("أعلى سعر اليوم", format="%.2f")
    low_price = st.number_input("أقل سعر اليوم", format="%.2f")
    close_prev = st.number_input("سعر إغلاق أمس", format="%.2f")
    volume = st.number_input("عدد الأسهم المتداولة اليوم", value=0)

    if st.button("تحليل يدوي"):
        liq_today = volume * open_price if volume>0 else 0
        s1 = low_price
        s2 = (low_price + open_price)/2
        r1 = high_price
        r2 = (high_price + open_price)/2

        trader_score = score_trader(50, open_price, s1)
        swing_score = score_swing(50)
        invest_score = 60

        st.markdown(f"""
        <div class="card">
        <h3>{symbol_manual}</h3>
        💰 السعر الحالي (Open): {open_price:.2f}<br>
        🧱 الدعم: {s1:.2f} / {s2:.2f}<br>
        🚧 المقاومة: {r1:.2f} / {r2:.2f}<br>
        💧 السيولة اليوم: {liq_today:,} جنيه
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
        🎯 <b>مضارب</b><br>
        <span class="score">{trader_score}/100</span><br>
        ⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f}
        </div>

        <div class="card">
        🔁 <b>سوينج</b><br>
        <span class="score">{swing_score}/100</span><br>
        🔁 حركة تصحيح، راقب الارتداد
        </div>

        <div class="card">
        🏦 <b>مستثمر</b><br>
        <span class="score">{invest_score}/100</span><br>
        🏦 اتجاه طويل الأجل إيجابي
        </div>
        """, unsafe_allow_html=True)

        whatsapp_msg_manual = f"""
📊 *تحليل سهم {symbol_manual} - يدوي*

💰 السعر الحالي: {open_price:.2f}
🧱 الدعم: {s1:.2f} / {s2:.2f}
🚧 المقاومة: {r1:.2f} / {r2:.2f}
💧 السيولة اليوم: {liq_today:,} جنيه

🎯 مضارب: {trader_score}/100
🔁 سوينج: {swing_score}/100
🏦 مستثمر: {invest_score}/100

⚠️ قرارك مسؤوليتك 😁
"""
        wa_url_manual = "https://wa.me/?text=" + urllib.parse.quote(whatsapp_msg_manual)
        st.markdown(f'<a href="{wa_url_manual}" class="whatsapp-btn" target="_blank">📲 مشاركة التحليل على واتساب</a>', unsafe_allow_html=True)

# TAB 3: Scanner
with tab3:
    st.subheader("🚨 فرص مضاربية قرب الدعم")
    alerts = scanner_watchlist()
    if alerts:
        for a in alerts:
            st.error(a)
    else:
        st.success("لا توجد فرص حالياً")
