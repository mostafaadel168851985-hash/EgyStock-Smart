import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse # دي لازم تكون هنا في الكود بس

# 1. المظهر (نفس شكل التليجرام)
st.set_page_config(page_title="EGX Sniper v111", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: bold; }
    .report-card {
        background: #ffffff; color: #000000 !important; padding: 20px; 
        border-radius: 15px; border: 4px solid #3498db; margin-top: 10px;
    }
    .report-card b, .report-card p, .report-card h3 { color: #000000 !important; }
    .wa-btn {
        display: flex; align-items: center; justify-content: center;
        background: #25D366; color: white !important; padding: 12px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 2. وظيفة التقرير (متصلحة عشان متطلعش فاضية)
def render_sniper_result(stock_name, p_now, p_high, p_low):
    # الحسابات
    piv = (p_now + p_high + p_low) / 3
    s1 = (2 * piv) - p_high
    s2 = piv - (p_high - p_low)
    r1 = (2 * piv) - p_low
    r2 = piv + (p_high - p_low)
    stop = s2 * 0.99

    # رسم التقرير
    st.markdown(f"""
    <div class="report-card">
        <h3 style="text-align: center;">💎 تقرير {stock_name}</h3>
        <p>💰 <b>السعر اللحظي:</b> {p_now:.2f}</p>
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
    
    # رسالة الواتساب
    wa_txt = f"تحليل {stock_name}:\nالسعر: {p_now:.2f}\nأهداف: {r1:.2f}-{r2:.2f}\nدعوم: {s1:.2f}-{s2:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_txt)}" class="wa-btn">📲 إرسال عبر واتساب</a>', unsafe_allow_html=True)

# 3. التابات جنب بعض
t_auto, t_manual = st.tabs(["📡 رادار آلي", "🛠️ إدخال يدوي"])

with t_auto:
    code = st.text_input("كود السهم:").upper().strip()
    if code:
        try:
            ticker = yf.Ticker(f"{code}.CA")
            df = ticker.history(period="1d")
            if not df.empty:
                render_sniper_result(code, df['Close'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1])
            else: st.error("❌ الآلي مش شايف داتا للسهم ده، جرب اليدوي.")
        except: st.error("❌ في مشكلة في الاتصال بالبورصة.")

with t_manual:
    st.write("حط الأرقام من الشاشة هنا:")
    c1, c2, c3 = st.columns(3)
    p_val = c1.number_input("السعر الآن", format="%.2f", min_value=0.0)
    h_val = c2.number_input("أعلى سعر", format="%.2f", min_value=0.0)
    l_val = c3.number_input("أقل سعر", format="%.2f", min_value=0.0)
    
    if p_val > 0 and h_val > 0:
        render_sniper_result("تحليل يدوي", p_val, h_val, l_val)
