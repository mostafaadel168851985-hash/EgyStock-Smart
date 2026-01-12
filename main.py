import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

# 1. إعدادات التصميم الاحترافي
st.set_page_config(page_title="EGX Sniper Elite v101", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: 900 !important; }
    input { background-color: #1e2732 !important; color: #FFFFFF !important; border: 2px solid #3498db !important; }
    /* تنسيق زرار الواتساب المودرن */
    .wa-button {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #25D366; color: white !important;
        padding: 15px 30px; border-radius: 50px; font-weight: bold;
        text-decoration: none; box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
        transition: 0.3s; width: 100%; margin-top: 20px;
    }
    .wa-button:hover { transform: scale(1.02); background-color: #1da851; }
</style>
""", unsafe_allow_html=True)

# 2. وظيفة عرض التقرير (موحدة للآلي واليدوي)
def display_report(ticker_name, p, hi, lo):
    piv = (p + hi + lo) / 3
    s1, s2 = (2 * piv) - hi, piv - (hi - lo)
    r1, r2 = (2 * piv) - lo, piv + (hi - lo)
    stop_loss = s2 * 0.99
    
    # الإشعارات
    if p <= (s1 * 1.005):
        st.success(f"🔥 فرصة دخول قوية: السهم عند الدعم {s1:.2f}")
    elif p >= (r1 * 0.995):
        st.error(f"🚀 إشارة بيع/تخفيف: السهم عند المقاومة {r1:.2f}")

    # كارت التقرير (شكل التليجرام)
    st.markdown(f"""
    <div style="background: #ffffff; color: #000000; padding: 25px; border-radius: 20px; font-family: 'Arial'; border: 3px solid #3498db;">
        <h2 style="text-align: center; color: #000; border-bottom: 2px solid #3498db; padding-bottom: 10px;">💎 التحليل الشامل لـ {ticker_name}</h2>
        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
            <span>💰 <b>السعر:</b> {p:.2f}</span>
            <span>💧 <b>السيولة:</b> طبيعية ⚖️</span>
        </div>
        <p>📢 <b>التوصية:</b> مراقبة عند الدعوم ⚖️</p>
        <hr>
        <p>🚀 <b>الأهداف (المقاومات):</b></p>
        <p style="color: #2ecc71;">🎯 هدف أول: {r1:.2f} | 🎯 هدف ثاني: {r2:.2f}</p>
        <hr>
        <p>🛡️ <b>مناطق الأمان (الدعوم):</b></p>
        <p style="color: #e67e22;">🔸 دعم أول: {s1:.2f} | 🔸 دعم ثاني: {s2:.2f}</p>
        <hr>
        <p style="color: #e74c3c;">🛑 <b>وقف الخسارة المعتمد: {stop_loss:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # زر الواتساب المودرن
    wa_msg = f"💎 تحليل {ticker_name}:\n💰 السعر: {p:.2f}\n🎯 أهداف: {r1:.2f} - {r2:.2f}\n🛡️ دعوم: {s1:.2f} - {s2:.2f}\n🛑 وقف: {stop_loss:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_msg)}" class="wa-button">💬 مشاركة التحليل الذكي (WhatsApp)</a>', unsafe_allow_html=True)

# 3. الواجهة
st.title("🎯 رادار القناص v101")

tab1, tab2 = st.tabs(["🔍 بحث آلي", "🛠️ تحليل يدوي كامل"])

with tab1:
    u_input = st.text_input("ادخل كود السهم (مثل ATQA):").upper().strip()
    if u_input:
        try:
            stock = yf.Ticker(f"{u_input}.CA")
            data = stock.history(period="1d")
            if not data.empty:
                p = data['Close'].iloc[-1]
                hi, lo = data['High'].iloc[-1], data['Low'].iloc[-1]
                display_report(u_input, p, hi, lo)
            else: st.warning("⚠️ لم نجد بيانات للسهم، استخدم التبويب اليدوي.")
        except: st.error("❌ خطأ في جلب البيانات.")

with tab2:
    st.write("أدخل بيانات الشاشة اللحظية لإنشاء التقرير:")
    c1, c2, c3 = st.columns(3)
    mp = c1.number_input("السعر الآن", format="%.2f", min_value=0.0)
    mh = c2.number_input("أعلى سعر", format="%.2f", min_value=0.0)
    ml = c3.number_input("أقل سعر", format="%.2f", min_value=0.0)
    
    if mp > 0 and mh > 0:
        display_report("تحليل يدوي", mp, mh, ml)
