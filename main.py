import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 1. إعدادات المظهر الفخم (أبيض ناصع وخطوط واضحة)
st.set_page_config(page_title="EGX Auto Sniper v106", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: bold; }
    .report-card {
        background: #ffffff; color: #000000; padding: 25px; 
        border-radius: 20px; border: 4px solid #3498db; font-family: 'Arial'; margin-top: 15px;
    }
    .report-card h3 { color: #1e2732 !important; text-align: center; border-bottom: 2px solid #3498db; }
    .wa-btn {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important; padding: 15px; border-radius: 12px;
        text-decoration: none; font-weight: bold; margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 2. مخزن الإشعارات
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# 3. محرك جلب البيانات "الخارق" (Anti-Block)
def fetch_auto_data(ticker):
    headers = {'User-Agent': 'Mozilla/5.0'}
    # المحاولة الأولى: Google Finance
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:EGX"
        soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
        price = float(soup.find("div", {"class": "YMlS1d"}).text.replace('EGP', '').replace(',', '').strip())
        # جلب الباقي من ياهو
        y_data = yf.Ticker(f"{ticker}.CA").history(period="1d")
        if not y_data.empty:
            return price, y_data['High'].iloc[-1], y_data['Low'].iloc[-1]
        return price, price, price
    except:
        # المحاولة الثانية: Yahoo Finance المباشر
        try:
            df = yf.Ticker(f"{ticker}.CA").history(period="1d")
            if not df.empty:
                return df['Close'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1]
        except: return None, None, None

# 4. دالة عرض التقرير الموحد
def generate_report(title, p, hi, lo):
    piv = (p + hi + lo) / 3
    s1, s2 = (2 * piv) - hi, piv - (hi - lo)
    r1, r2 = (2 * piv) - lo, piv + (hi - lo)
    stop_loss = s2 * 0.99
    
    is_buy = p <= (s1 * 1.01)
    if is_buy:
        alert_msg = f"🔔 فرصة دخول: {title} عند دعم {s1:.2f}"
        if alert_msg not in st.session_state.alerts:
            st.session_state.alerts.append(alert_msg)

    st.markdown(f"""
    <div class="report-card">
        <h3>💎 تقرير {title} اللحظي</h3>
        <p>💰 <b>السعر اللحظي:</b> {p:.2f} | <b>الحالة:</b> {'🔥 دخول' if is_buy else '⚖️ مراقبة'}</p>
        <hr>
        <p style="color: #2ecc71;">🚀 <b>المستهدفات:</b> {r1:.2f} - {r2:.2f}</p>
        <p style="color: #e67e22;">🛡️ <b>الدعوم:</b> {s1:.2f} - {s2:.2f}</p>
        <p style="color: #e74c3c;">🛑 <b>وقف الخسارة: {stop_loss:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    wa_msg = f"تحليل {title}:\nالسعر: {p:.2f}\nأهداف: {r1:.2f}-{r2:.2f}\nدعوم: {s1:.2f}-{s2:.2f}\nوقف: {stop_loss:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_msg)}" class="wa-btn">📲 مشاركة عبر واتساب</a>', unsafe_allow_html=True)

# 5. الواجهة الثلاثية
st.title("🏹 قناص البورصة الآلي v106")
tab_auto, tab_manual, tab_alerts = st.tabs(["📡 البحث الآلي", "🛠️ الطوارئ (يدوي)", "🔔 رادار الإشعارات"])

with tab_auto:
    u_input = st.text_input("🔍 ادخل كود السهم (مثل ATQA):").upper().strip()
    if u_input:
        with st.spinner('⏳ جاري جلب الداتا آلياً...'):
            p, hi, lo = fetch_auto_data(u_input)
            if p: generate_report(u_input, p, hi, lo)
            else: st.error("❌ المواقع العالمية محجوبة حالياً، استخدم تاب الطوارئ.")

with tab_manual:
    st.info("استخدم ده لو الآلي عطلان عشان تطلع التقرير فوراً")
    c1, c2, c3 = st.columns(3)
    p_in = c1.number_input("السعر الآن", format="%.2f", key="pm")
    h_in = c2.number_input("أعلى سعر", format="%.2f", key="hm")
    l_in = c3.number_input("أقل سعر", format="%.2f", key="lm")
    if p_in > 0: generate_report("تحليل يدوي", p_in, h_in, l_in)

with tab_alerts:
    st.subheader("🔔 الأسهم اللي عند منطقة دعم")
    if st.session_state.alerts:
        for a in st.session_state.alerts: st.success(a)
    else: st.write("مفيش إشعارات حالياً.")
