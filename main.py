import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse
import requests

# 1. المظهر الاحترافي والتابات
st.set_page_config(page_title="EGX Sniper Elite v107", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: bold; }
    .report-card {
        background: #ffffff; color: #000000; padding: 25px; 
        border-radius: 20px; border: 4px solid #3498db; font-family: 'Arial'; margin-top: 15px;
    }
    .report-card h3 { color: #1e2732 !important; text-align: center; border-bottom: 2px solid #3498db; margin-bottom: 15px;}
    .wa-btn {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important; padding: 18px; border-radius: 15px;
        text-decoration: none; font-weight: bold; margin-top: 20px;
        box-shadow: 0 4px 15px rgba(18,140,126,0.3); font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# 2. نظام تخزين الإشعارات
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# 3. محرك جلب البيانات المطور (الآلي)
def get_live_data(ticker):
    try:
        t_ca = f"{ticker}.CA"
        # استخدام جلسة مخصصة لتجنب الحظر
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        stock = yf.Ticker(t_ca, session=session)
        # جلب السعر اللحظي
        p = stock.fast_info['last_price']
        
        # جلب الهاي واللو لليوم
        df = stock.history(period="1d")
        if not df.empty:
            return p, df['High'].iloc[-1], df['Low'].iloc[-1]
        return p, p, p
    except:
        return None, None, None

# 4. دالة عرض التقرير (تليجرام + واتساب)
def display_full_report(name, p, hi, lo):
    piv = (p + hi + lo) / 3
    s1, s2 = (2 * piv) - hi, piv - (hi - lo)
    r1, r2 = (2 * piv) - lo, piv + (hi - lo)
    stop_loss = s2 * 0.99
    
    # الإشعارات الذكية
    if p <= (s1 * 1.005):
        msg = f"🔔 فرصة دخول: {name} عند دعم {s1:.2f}"
        if msg not in st.session_state.alerts: st.session_state.alerts.append(msg)
        st.success(msg)

    # التقرير الأبيض
    st.markdown(f"""
    <div class="report-card">
        <h3>💎 تقرير {name} التحليلي</h3>
        <p>💰 <b>السعر الحالي:</b> {p:.2f}</p>
        <p>📢 <b>التوصية اللحظية:</b> {'🔥 شراء دخول' if p <= (s1 * 1.01) else '⚖️ مراقبة وتحفظ'}</p>
        <hr>
        <p style="color: #2ecc71; font-size: 18px;">🚀 <b>مستويات الأهداف:</b></p>
        <p>🎯 هدف 1: {r1:.2f} | 🎯 هدف 2: {r2:.2f}</p>
        <hr>
        <p style="color: #e67e22; font-size: 18px;">🛡️ <b>مستويات الدعوم:</b></p>
        <p>🔸 دعم 1: {s1:.2f} | 🔸 دعم 2: {s2:.2f}</p>
        <hr>
        <p style="color: #e74c3c; font-size: 18px;">🛑 <b>وقف الخسارة: {stop_loss:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # زر الواتساب المودرن
    wa_msg = f"💎 تحليل {name}:\n💰 السعر: {p:.2f}\n🎯 أهداف: {r1:.2f} - {r2:.2f}\n🛡️ دعوم: {s1:.2f} - {s2:.2f}\n🛑 وقف: {stop_loss:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_msg)}" class="wa-btn">📲 مشاركة التقرير (WhatsApp)</a>', unsafe_allow_html=True)

# 5. تابات البرنامج (جنب بعض)
st.title("🏹 رادار قناص البورصة v107")
tab_auto, tab_manual, tab_alerts = st.tabs(["📡 البحث الآلي", "🛠️ الطوارئ (يدوي)", "🔔 رادار الإشعارات"])

with tab_auto:
    ticker = st.text_input("ادخل كود السهم (مثلاً TMGH):").upper().strip()
    if ticker:
        with st.spinner('⏳ جاري سحب الداتا آلياً...'):
            p, hi, lo = get_live_data(ticker)
            if p: display_full_report(ticker, p, hi, lo)
            else: st.error("❌ عطل مؤقت في الداتا الآلية.. استخدم اليدوي فوراً.")

with tab_manual:
    st.info("حط بيانات الشاشة لو الآلي اتأخر")
    c1, c2, c3 = st.columns(3)
    mp = c1.number_input("السعر الآن", format="%.2f", key="m_p")
    mh = c2.number_input("أعلى اليوم", format="%.2f", key="m_h")
    ml = c3.number_input("أقل اليوم", format="%.2f", key="m_l")
    if mp > 0: display_full_report("تحليل يدوي", mp, mh, ml)

with tab_alerts:
    st.subheader("🔔 الأسهم المكتشفة عند الدعم")
    if st.session_state.alerts:
        for alert in st.session_state.alerts: st.success(alert)
    else: st.write("لا توجد إشعارات حالياً.")
