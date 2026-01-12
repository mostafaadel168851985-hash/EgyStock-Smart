import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

# 1. المظهر الاحترافي والتابات
st.set_page_config(page_title="EGX Sniper v108", layout="centered")

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
        color: white !important; padding: 18px; border-radius: 15px;
        text-decoration: none; font-weight: bold; margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 2. نظام حفظ الأسهم (للإشعارات)
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# 3. محرك جلب الداتا (محاولة الربط المباشر)
def get_data_auto(ticker):
    try:
        # بنجرب نسحب الداتا بأكثر من طريقة
        stock = yf.Ticker(f"{ticker}.CA")
        df = stock.history(period="1d", interval="1m") # سحب داتا الدقيقة
        if df.empty:
            df = stock.history(period="1d")
            
        if not df.empty:
            p = df['Close'].iloc[-1]
            hi = df['High'].max()
            lo = df['Low'].min()
            return p, hi, lo
        return None, None, None
    except:
        return None, None, None

# 4. دالة عرض التقرير
def show_report(name, p, hi, lo):
    piv = (p + hi + lo) / 3
    s1, s2 = (2 * piv) - hi, piv - (hi - lo)
    r1, r2 = (2 * piv) - lo, piv + (hi - lo)
    
    # فحص الدخول (إشعارات)
    if p <= (s1 * 1.01):
        st.success(f"🔥 إشارة قناص: {name} عند منطقة دعم ({s1:.2f})")
        if name not in st.session_state.watchlist:
            st.session_state.watchlist.append({"name": name, "price": p, "s1": s1})

    st.markdown(f"""
    <div class="report-card">
        <h2 style="text-align: center; border-bottom: 2px solid #3498db;">💎 تقرير {name}</h2>
        <p style="font-size: 20px;">💰 <b>السعر اللحظي:</b> {p:.2f}</p>
        <hr>
        <p style="color: #2ecc71 !important;">🚀 <b>الأهداف:</b> {r1:.2f} - {r2:.2f}</p>
        <p style="color: #e67e22 !important;">🛡️ <b>الدعوم:</b> {s1:.2f} - {s2:.2f}</p>
        <p style="color: #e74c3c !important;">🛑 <b>وقف الخسارة: {s2 * 0.99:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    msg = f"تحليل {name}:\nالسعر: {p:.2f}\nأهداف: {r1:.2f}-{r2:.2f}\nدعوم: {s1:.2f}-{s2:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" class="wa-btn">📲 مشاركة عبر واتساب</a>', unsafe_allow_html=True)

# 5. الواجهة بالتابات
st.title("🏹 رادار قناص البورصة v108")
t_auto, t_man, t_alert = st.tabs(["📡 آلي", "🛠️ يدوي", "🔔 الإشعارات"])

with t_auto:
    symbol = st.text_input("كود السهم:").upper().strip()
    if symbol:
        with st.spinner('⏳ بحاول أخترق الحجب وأجيب السعر...'):
            p, hi, lo = get_data_auto(symbol)
            if p: show_report(symbol, p, hi, lo)
            else: st.error("❌ السيرفر لسه محجوب من المواقع العالمية.. جرب اليدوي دلوقت.")

with t_man:
    c1, c2, c3 = st.columns(3)
    p_m = c1.number_input("السعر", format="%.2f", key="p1")
    h_m = c2.number_input("أعلى", format="%.2f", key="h1")
    l_m = c3.number_input("أقل", format="%.2f", key="l1")
    if p_m > 0: show_report("تحليل يدوي", p_m, h_m, l_m)

with t_alert:
    st.subheader("🔔 فرص تم رصدها")
    if st.session_state.watchlist:
        for item in st.session_state.watchlist:
            st.info(f"السهم: {item['name']} | السعر: {item['price']} | دعم: {item['s1']:.2f}")
    else: st.write("ابحث عن أسهم أولاً!")
