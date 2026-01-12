import streamlit as st
import pandas as pd
import urllib.parse
import requests

# 1. تنسيق الواجهة (التقرير الأبيض والتابات)
st.set_page_config(page_title="EGX Sniper v115", layout="centered")

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

# 2. مخزن الإشعارات
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# 3. محرك جلب الداتا "المخترق" (استخدام API بديل مجاني)
def get_auto_data_v2(ticker):
    try:
        # بنجرب نكلم Yahoo عبر رابط JSON مباشر (ده أحياناً بيفلت من الحظر)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.CA?interval=1d&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
        response = requests.get(url, headers=headers).json()
        
        result = response['chart']['result'][0]
        price = result['indicators']['quote'][0]['close'][0]
        high = result['indicators']['quote'][0]['high'][0]
        low = result['indicators']['quote'][0]['low'][0]
        
        return price, high, low
    except:
        return None, None, None

# 4. دالة عرض التقرير الموحد
def display_final_report(name, p, hi, lo):
    piv = (p + hi + lo) / 3
    s1, r1 = (2 * piv) - hi, (2 * piv) - lo
    s2, r2 = piv - (hi - lo), piv + (hi - lo)
    stop = s2 * 0.99
    
    # فحص الإشعارات (عند الدعم)
    if p <= (s1 * 1.01):
        alert_msg = f"🔔 فرصة دخول: {name} عند دعم {s1:.2f}"
        if alert_msg not in st.session_state.alerts:
            st.session_state.alerts.append(alert_msg)

    st.markdown(f"""
    <div class="report-card">
        <h3 style="text-align: center;">💎 تحليل {name} الآلي</h3>
        <p style="font-size: 20px;">💰 <b>السعر اللحظي:</b> {p:.2f}</p>
        <hr>
        <p style="color: #2ecc71 !important;">🚀 <b>الأهداف:</b> {r1:.2f} - {r2:.2f}</p>
        <p style="color: #e67e22 !important;">🛡️ <b>الدعوم:</b> {s1:.2f} - {s2:.2f}</p>
        <hr>
        <p style="color: #e74c3c !important;">🛑 <b>وقف الخسارة: {stop:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    wa_msg = f"تحليل {name}:\nالسعر: {p:.2f}\nأهداف: {r1:.2f}-{r2:.2f}\nدعوم: {s1:.2f}-{s2:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_msg)}" class="wa-btn">📲 مشاركة عبر واتساب</a>', unsafe_allow_html=True)

# 5. التابات
st.title("🏹 رادار قناص البورصة v115")
tab1, tab2, tab3 = st.tabs(["📡 رادار آلي", "🛠️ يدوي للطوارئ", "🔔 الإشعارات"])

with tab1:
    code = st.text_input("ادخل كود السهم:").upper().strip()
    if code:
        with st.spinner('⏳ جاري محاولة جلب الداتا عبر رابط مباشر...'):
            p, hi, lo = get_auto_data_v2(code)
            if p:
                display_final_report(code, p, hi, lo)
            else:
                st.error("❌ الحظر لسه موجود. السيرفر محظور من مصدر الداتا الرئيسي.")

with tab2:
    c1, c2, c3 = st.columns(3)
    p_in = c1.number_input("السعر الآن", format="%.2f", key="p_v115")
    h_in = c2.number_input("أعلى سعر", format="%.2f", key="h_v115")
    l_in = c3.number_input("أقل سعر", format="%.2f", key="l_v115")
    if p_in > 0:
        display_final_report("تحليل يدوي", p_in, h_in, l_in)

with tab3:
    st.subheader("🔔 الأسهم اللي لمست مناطق الدعم")
    if st.session_state.alerts:
        for a in st.session_state.alerts:
            st.success(a)
    else:
        st.write("لا توجد إشعارات حالياً.")
