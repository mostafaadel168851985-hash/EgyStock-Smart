import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import urllib.parse
import time

# =====================
# CONFIGURATION
# =====================
st.set_page_config(page_title="EGX Sniper PRO", layout="centered")

WATCHLIST = ["TMGH.CA", "COMI.CA", "ETEL.CA", "SWDY.CA", "EFID.CA"]

COMPANIES = {
    "TMGH.CA": "طلعت مصطفى",
    "COMI.CA": "البنك التجاري الدولي",
    "ETEL.CA": "المصرية للاتصالات",
    "SWDY.CA": "السويدي إليكتريك",
    "EFID.CA": "إيديتا"
}

# =====================
# STYLING
# =====================
st.markdown("""
<style>
body { background-color: #0e1117; color: #ffffff; }
.card { background-color:#161b22; padding:20px; border-radius:15px; margin-bottom:20px; }
.score { font-size:26px; font-weight:bold; }
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

# =====================
# FUNCTIONS
# =====================
def load_data(symbol):
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

# ===== Score calculation =====
def score_trader(rsi_val, price, support):
    score = 50
    if rsi_val < 30: score += 20
    if abs(price - support)/support < 0.02: score += 15
    return min(score, 100)

def score_swing(rsi_val):
    return min(100, 60 + (50 - abs(50 - rsi_val)))

def score_invest(df):
    ma50 = df['Close'].rolling(50).mean().iloc[-1]
    price = df['Close'].iloc[-1]
    return 80 if price > ma50 else 55

# ===== AI Comments =====
def ai_comment_trader(price, s1):
    return f"⚡ مناسب لمضاربة سريعة قرب الدعم {s1:.2f} مع الالتزام بوقف الخسارة."

def ai_comment_swing():
    return "🔁 السهم في حركة تصحيح داخل اتجاه عام، مراقبة الارتداد مطلوبة."

def ai_comment_invest():
    return "🏦 الاتجاه طويل الأجل إيجابي طالما السعر أعلى المتوسط 50 يوم."

# =====================
# SCANNER
# =====================
def scanner_watchlist():
    alerts = []
    for symbol in WATCHLIST:
        df = load_data(symbol)
        if df is None: continue
        price = df['Close'].iloc[-1]
        rsi_val = rsi(df['Close']).iloc[-1]
        s1, s2, r1, r2 = support_resistance(df)
        if price <= s1*1.02 and rsi_val < 40:
            alerts.append(f"🚨 {symbol} ({COMPANIES.get(symbol,'')}) | السعر: {price:.2f} | دعم: {s1:.2f} | هدف: {r1:.2f}")
    return alerts

# =====================
# UI
# =====================
st.title("🏹 EGX Sniper PRO")

tab1, tab2, tab3 = st.tabs(["📡 تحليل لحظي", "🛠️ يدوي", "🚨 Scanner"])

with tab1:
    symbol = st.text_input("🧾 كود السهم (مثال: TMGH.CA)", "").upper().strip()
    refresh = st.slider("تحديث (ثواني)", 5, 60, 15)

    if symbol:
        df = load_data(symbol)
        if df is None:
            st.error("⚠️ فشل جلب البيانات")
        else:
            price = df['Close'].iloc[-1]
            rsi_val = rsi(df['Close']).iloc[-1]
            s1, s2, r1, r2 = support_resistance(df)
            liq_today, liq_avg = liquidity(df)
            company_name = COMPANIES.get(symbol, "")

            trader_score = score_trader(rsi_val, price, s1)
            swing_score = score_swing(rsi_val)
            invest_score = score_invest(df)

            # ====== CARD ======
            st.markdown(f"""
            <div class="card">
            <h3>{symbol} - {company_name}</h3>
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

            # ===== WhatsApp button =====
            whatsapp_msg = f"""
📊 *تحليل سهم {symbol} - {company_name}*

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

            # ===== Auto-refresh =====
            time.sleep(refresh)
            st.experimental_rerun()

with tab2:
    c1, c2, c3, c4 = st.columns(4)
    p = c1.number_input("السعر", format="%.2f")
    h = c2.number_input("أعلى", format="%.2f")
    l = c3.number_input("أقل", format="%.2f")
    v = c4.number_input("حجم التداول")
    if p > 0:
        df_manual = pd.DataFrame({'Close':[p], 'High':[h], 'Low':[l], 'Volume':[v]})
        s1, s2, r1, r2 = support_resistance(df_manual)
        liq_today, liq_avg = liquidity(df_manual)
        st.write("✅ تحليل يدوي جاهز")

with tab3:
    st.subheader("🚨 فرص مضاربية قرب الدعم")
    alerts = scanner_watchlist()
    if alerts:
        for a in alerts:
            st.error(a)
    else:
        st.success("لا توجد فرص حالياً")
