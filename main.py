import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse
import requests

# 1. المظهر (نفس شكل التليجرام الشيك)
st.set_page_config(page_title="EGX Sniper v112", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: bold; }
    .report-card {
        background: #ffffff; color: #000000 !important; padding: 20px; 
        border-radius: 15px; border: 3px solid #3498db; margin-top: 10px;
    }
    .report-card * { color: #000000 !important; }
    .wa-btn {
        display: flex; align-items: center; justify-content: center;
        background: #25D366; color: white !important; padding: 12px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 2. وظيفة التقرير (اللي شغالة معاك في اليدوي)
def render_report(name, p, hi, lo):
    piv = (p + hi + lo) / 3
    s1, r1 = (2 * piv) - hi, (2 * piv) - lo
    s2, r2 = piv - (hi - lo), piv + (hi - lo)
    stop = s2 * 0.99

    st.markdown(f"""
    <div class="report-card">
        <h3 style="text-align: center;">💎 تقرير تحليل {name}</h3>
        <p>💰 <b>السعر اللحظي:</b> {p:.2f}</p>
        <hr>
        <p style="color: #2ecc71 !important;">🚀 <b>الأهداف اللحظية:</b></p>
        <p>🎯 هدف 1: {r1:.2f} | 🎯 هدف 2: {r2:.2f}</p>
        <hr>
        <p style="color: #e67e22 !important;">🛡️ <b>مناطق الدعم:</b></p>
        <p>🔸 دعم 1: {s1:.2f} | 🔸 دعم 2: {s2:.2f}</p>
        <hr>
        <p style="color: #e74c3c !important;">🛑 <b>وقف الخسارة: {stop:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    wa_txt = f"تحليل {name}:\nالسعر: {p:.2f}\nأهداف: {r1:.2f}-{r2:.2f}\nدعوم: {s1:.2f}-{s2:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_txt)}" class="wa-btn">📲 إرسال عبر واتساب</a>', unsafe_allow_html=True)

# 3. محرك البحث الآلي (بتعديل فك الحظر)
def get_auto_data(symbol):
    try:
        # خدعة الـ Header لفك حظر ياهو
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15'})
        
        ticker = yf.Ticker(f"{symbol}.CA", session=session)
        df = ticker.history(period="1d", interval="1m") # طلب داتا دقيقة بدقيقة
        if df.empty:
            df = ticker.history(period="1d")
            
        if not df.empty:
            return df['Close'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1]
        return None, None, None
    except:
        return None, None, None

# 4. التابات
t_auto, t_manual = st.tabs(["📡 رادار آلي", "🛠️ إدخال يدوي"])

with t_auto:
    code = st.text_input("كود السهم (ATQA, TMGH):").upper().strip()
    if code:
        with st.spinner('⏳ بحاول أجيب السعر اللحظي...'):
            p, hi, lo = get_auto_data(code)
            if p: render_report(code, p, hi, lo)
            else: st.error("⚠️ ياهو لسه قافل الداتا الآلية على السيرفر ده. استخدم اليدوي حالياً.")

with t_manual:
    c1, c2, c3 = st.columns(3)
    p_in = c1.number_input("السعر", format="%.2f", key="p2")
    h_in = c2.number_input("أعلى", format="%.2f", key="h2")
    l_in = c3.number_input("أقل", format="%.2f", key="l2")
    if p_in > 0: render_report("تحليل يدوي", p_in, h_in, l_in)
