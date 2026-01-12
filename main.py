import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

# 1. تنسيق الواجهة (أبيض ناصع للتقرير)
st.set_page_config(page_title="EGX Sniper v110", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: bold; }
    .report-card {
        background: #ffffff; color: #000000 !important; padding: 20px; 
        border-radius: 15px; border: 3px solid #3498db; margin-top: 10px;
    }
    .report-card b, .report-card p, .report-card h3 { color: #000000 !important; }
    .wa-btn {
        display: flex; align-items: center; justify-content: center;
        background: #25D366; color: white !important; padding: 12px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 2. محرك الحسابات (إصلاح مشكلة التقرير الفاضي)
def show_sniper_report(name, price, high, low):
    # معادلات البيفوت (Pivot)
    pivot = (price + high + low) / 3
    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    r1 = (2 * pivot) - low
    r2 = pivot + (high - low)
    stop = s2 * 0.99

    # تصميم التقرير (نفس شكل التليجرام)
    st.markdown(f"""
    <div class="report-card">
        <h3 style="text-align: center;">💎 تحليل {name}</h3>
        <p>💰 <b>السعر الآن:</b> {price:.2f}</p>
        <hr style="border: 0.5px solid #eee">
        <p style="color: #2ecc71 !important;">🚀 <b>الأهداف اللحظية:</b></p>
        <p>🎯 هدف 1: {r1:.2f} | 🎯 هدف 2: {r2:.2f}</p>
        <hr style="border: 0.5px solid #eee">
        <p style="color: #e67e22 !important;">🛡️ <b>مناطق الدعم:</b></p>
        <p>🔸 دعم 1: {s1:.2f} | 🔸 دعم 2: {s2:.2f}</p>
        <hr style="border: 0.5px solid #eee">
        <p style="color: #e74c3c !important;">🛑 <b>وقف الخسارة: {stop:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # زر الواتساب المباشر
    wa_text = f"تحليل {name}:\nالسعر: {price:.2f}\nأهداف: {r1:.2f}-{r2:.2f}\nدعوم: {s1:.2f}-{s2:.2f}\nوقف: {stop:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_text)}" class="wa-btn">📲 مشاركة عبر واتساب</a>', unsafe_allow_html=True)

# 3. التابات
tab_auto, tab_manual, tab_alerts = st.tabs(["📡 آلي", "🛠️ يدوي", "🔔 إشعارات"])

with tab_auto:
    symbol = st.text_input("ادخل الكود (مثلاً ATQA):").upper().strip()
    if symbol:
        try:
            # محاولة جلب الداتا آلياً
            data = yf.Ticker(f"{symbol}.CA").history(period="1d")
            if not data.empty:
                curr_p = data['Close'].iloc[-1]
                high_p = data['High'].iloc[-1]
                low_p = data['Low'].iloc[-1]
                show_sniper_report(symbol, curr_p, high_p, low_p)
            else:
                st.error("❌ عطل في جلب السعر اللحظي.. استخدم اليدوي حالياً.")
        except:
            st.error("❌ مشكلة في الاتصال بالبورصة.")

with tab_manual:
    st.write("أدخل أرقام الشاشة لملء التقرير:")
    c1, c2, c3 = st.columns(3)
    p_in = c1.number_input("السعر الآن", format="%.2f", key="p_m")
    h_in = c2.number_input("أعلى اليوم", format="%.2f", key="h_m")
    l_in = c3.number_input("أقل اليوم", format="%.2f", key="l_m")
    
    if p_in > 0 and h_in > 0:
        show_sniper_report("يدوي", p_in, h_in, l_in)

with tab_alerts:
    st.info("الأسهم التي تلمس الدعم ستظهر هنا قريباً")
