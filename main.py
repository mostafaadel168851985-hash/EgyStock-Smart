import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

# 1. إعدادات التصميم (Modern & Smart)
st.set_page_config(page_title="EGX Sniper v109", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: bold; }
    .report-card {
        background: #ffffff; color: #000000 !important; padding: 25px; 
        border-radius: 20px; border: 4px solid #3498db; font-family: 'Arial'; margin-top: 15px;
    }
    .report-card * { color: #000000 !important; }
    .wa-btn {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important; padding: 15px; border-radius: 50px;
        text-decoration: none; font-weight: bold; margin-top: 20px;
        box-shadow: 0 4px 15px rgba(37,211,102,0.3);
    }
</style>
""", unsafe_allow_html=True)

if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# 2. دالة الحسابات والتقرير (تصحيح اليدوي الفاضي)
def show_full_report(name, p, hi, lo):
    if p <= 0 or hi <= 0 or lo <= 0:
        st.warning("⚠️ يرجى التأكد من إدخال أرقام صحيحة (أكبر من صفر)")
        return

    # معادلات الـ Pivot Points الصحيحة
    piv = (p + hi + lo) / 3
    s1, s2 = (2 * piv) - hi, piv - (hi - lo)
    r1, r2 = (2 * piv) - lo, piv + (hi - lo)
    stop_loss = s2 * 0.99

    # الإشعارات
    if p <= (s1 * 1.01):
        msg = f"🔔 فرصة دخول: {name} عند دعم {s1:.2f}"
        if msg not in st.session_state.alerts: st.session_state.alerts.append(msg)
        st.success(msg)

    # كارت التقرير
    st.markdown(f"""
    <div class="report-card">
        <h2 style="text-align: center; border-bottom: 2px solid #3498db;">💎 تحليل {name}</h2>
        <p style="font-size: 18px;">💰 <b>السعر الآن:</b> {p:.2f}</p>
        <hr>
        <p style="color: #2ecc71 !important;">🚀 <b>الأهداف اللحظية:</b></p>
        <p>🎯 هدف 1: {r1:.2f} | 🎯 هدف 2: {r2:.2f}</p>
        <hr>
        <p style="color: #e67e22 !important;">🛡️ <b>مناطق الدعم (الأمان):</b></p>
        <p>🔸 دعم 1: {s1:.2f} | 🔸 دعم 2: {s2:.2f}</p>
        <hr>
        <p style="color: #e74c3c !important;">🛑 <b>وقف خسارة نهائي: {stop_loss:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # زر الواتساب
    wa_msg = f"💎 تحليل {name}:\n💰 السعر: {p:.2f}\n🎯 أهداف: {r1:.2f}-{r2:.2f}\n🛡️ دعوم: {s1:.2f}-{s2:.2f}\n🛑 وقف: {stop_loss:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_msg)}" class="wa-btn">💬 مشاركة عبر واتساب</a>', unsafe_allow_html=True)

# 3. الواجهة الثلاثية
st.title("🏹 رادار قناص البورصة v109")
t_auto, t_man, t_alert = st.tabs(["📡 آلي", "🛠️ يدوي", "🔔 الإشعارات"])

with t_auto:
    symbol = st.text_input("كود السهم (مثل ATQA):").upper().strip()
    if symbol:
        try:
            stock = yf.Ticker(f"{symbol}.CA")
            df = stock.history(period="1d")
            if not df.empty:
                show_full_report(symbol, df['Close'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1])
            else: st.error("❌ تعذر جلب الداتا الآلية.. استخدم اليدوي.")
        except: st.error("❌ مشكلة في الاتصال بالبورصة.")

with t_man:
    st.info("أدخل أرقام الشاشة لملء التقرير:")
    c1, c2, c3 = st.columns(3)
    p_in = c1.number_input("السعر الحالي", format="%.2f", step=0.01)
    h_in = c2.number_input("أعلى سعر", format="%.2f", step=0.01)
    l_in = c3.number_input("أقل سعر", format="%.2f", step=0.01)
    if p_in > 0:
        show_full_report("تحليل يدوي", p_in, h_in, l_in)

with t_alert:
    if st.session_state.alerts:
        for a in st.session_state.alerts: st.success(a)
    else: st.write("لا توجد إشعارات حالياً.")
