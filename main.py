import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 1. إعدادات التصميم (أبيض ناصع + Dark Mode)
st.set_page_config(page_title="EGX Auto Sniper v103", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: 900 !important; }
    input { background-color: #1e2732 !important; color: #FFFFFF !important; border: 2px solid #3498db !important; }
    
    /* زرار واتساب Modern & Smart */
    .wa-button {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important; padding: 15px; border-radius: 50px;
        font-weight: bold; text-decoration: none; margin-top: 20px;
        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3); transition: 0.3s;
    }
    .wa-button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# 2. محرك جلب البيانات الذكي (الآلي)
def get_auto_data(ticker):
    ticker_ca = f"{ticker}.CA"
    try:
        # الطريقة الأولى: Fast Info (الأسرع)
        stock = yf.Ticker(ticker_ca)
        info = stock.fast_info
        p = info['last_price']
        
        # جلب الهاي واللو
        df = stock.history(period="1d")
        if not df.empty:
            return p, df['High'].iloc[-1], df['Low'].iloc[-1]
        return p, p, p
    except:
        return None, None, None

# 3. دالة عرض التقرير (نفس شكل التليجرام)
def show_telegram_report(name, p, hi, lo):
    piv = (p + hi + lo) / 3
    s1, s2 = (2 * piv) - hi, piv - (hi - lo)
    r1, r2 = (2 * piv) - lo, piv + (hi - lo)
    stop_loss = s2 * 0.98
    
    # الإشعارات الملونة
    if p <= (s1 * 1.005):
        st.success(f"🔥 فرصة دخول: السهم عند الدعم {s1:.2f}")
    elif p >= (r1 * 0.995):
        st.error(f"🚀 إشارة بيع: السهم عند المقاومة {r1:.2f}")

    # كارت التقرير الأبيض
    st.markdown(f"""
    <div style="background: #ffffff; color: #000000; padding: 25px; border-radius: 15px; border: 3px solid #3498db; font-family: Arial;">
        <h2 style="text-align: center; color: #1e2732; border-bottom: 2px solid #3498db;">💎 تقرير الأداء لـ {name}</h2>
        <p style="font-size: 18px;">💰 <b>السعر اللحظي:</b> {p:.2f}</p>
        <hr>
        <p style="color: #2ecc71; font-weight: bold;">🚀 المستهدفات (أهدافك):</p>
        <p>🎯 هدف أول: {r1:.2f} | 🎯 هدف ثاني: {r2:.2f}</p>
        <hr>
        <p style="color: #e67e22; font-weight: bold;">🛡️ الدعوم (الأمان):</p>
        <p>🔸 دعم أول: {s1:.2f} | 🔸 دعم ثاني: {s2:.2f}</p>
        <hr>
        <p style="color: #e74c3c; font-size: 18px;">🛑 <b>وقف الخسارة: {stop_loss:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # زر الواتساب المودرن
    msg = f"💎 تحليل {name}:\n💰 السعر: {p:.2f}\n🎯 أهداف: {r1:.2f} - {r2:.2f}\n🛡️ دعوم: {s1:.2f} - {s2:.2f}\n🛑 وقف: {stop_loss:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" class="wa-button">📲 مشاركة التحليل الذكي (WhatsApp)</a>', unsafe_allow_html=True)

# 4. واجهة البرنامج
st.title("🎯 رادار القناص الآلي v103")

u_input = st.text_input("🔍 ادخل كود السهم (مثل ATQA أو TMGH):").upper().strip()

if u_input:
    with st.spinner('⏳ جاري سحب البيانات آلياً...'):
        p, hi, lo = get_auto_data(u_input)
    
    if p:
        show_telegram_report(u_input, p, hi, lo)
    else:
        st.error("⚠️ فشل جلب البيانات آلياً (حظر مؤقت). استخدم اليدوي بالأسفل فوراً.")

# 5. اليدوي (كامل)
st.markdown("---")
with st.expander("🛠️ لوحة الإدخال اليدوي (لو الآلي معلق)"):
    c1, c2, c3 = st.columns(3)
    mp = c1.number_input("السعر الآن", format="%.2f", key="man_p")
    mh = c2.number_input("أعلى اليوم", format="%.2f", key="man_h")
    ml = c3.number_input("أقل اليوم", format="%.2f", key="man_l")
    if mp > 0:
        show_telegram_report("تحليل يدوي", mp, mh, ml)
