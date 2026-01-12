import streamlit as st
import pandas as pd
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 1. المظهر الاحترافي
st.set_page_config(page_title="EGX Sniper v113", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: bold; }
    .report-card {
        background: #ffffff; color: #000000 !important; padding: 25px; 
        border-radius: 20px; border: 4px solid #3498db; margin-top: 15px;
    }
    .report-card * { color: #000000 !important; }
    .wa-btn {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important; padding: 18px; border-radius: 15px;
        text-decoration: none; font-weight: bold; margin-top: 20px;
        box-shadow: 0 4px 15px rgba(18,140,126,0.3);
    }
</style>
""", unsafe_allow_html=True)

# 2. محرك جلب البيانات من جوجل (بديل ياهو المحظور)
def fetch_from_google(ticker):
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:EGX"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # خطف السعر
        price_tag = soup.find("div", {"class": "YMlS1d"})
        price = float(price_tag.text.replace('EGP', '').replace(',', '').strip())
        
        # خطف الهاي واللو (من قسم Range)
        range_tags = soup.find_all("div", {"class": "P66Qp"})
        # جوجل بيعرض الهاي واللو في أول ديف غالباً
        day_range = range_tags[0].text.split(' - ')
        lo = float(day_range[0].replace(',', '').strip())
        hi = float(day_range[1].replace(',', '').strip())
        
        return price, hi, lo
    except:
        return None, None, None

# 3. دالة عرض التقرير
def display_report(name, p, hi, lo):
    piv = (p + hi + lo) / 3
    s1, r1 = (2 * piv) - hi, (2 * piv) - lo
    s2, r2 = piv - (hi - lo), piv + (hi - lo)
    stop = s2 * 0.99

    st.markdown(f"""
    <div class="report-card">
        <h3 style="text-align: center;">💎 تحليل {name} (آلي)</h3>
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

# 4. الواجهة
st.title("🏹 قناص البورصة v113")
tab_auto, tab_manual = st.tabs(["📡 رادار آلي (جوجل)", "🛠️ إدخال يدوي"])

with tab_auto:
    code = st.text_input("كود السهم (مثل ATQA):").upper().strip()
    if code:
        with st.spinner('⏳ جاري سحب البيانات من جوجل...'):
            p, hi, lo = fetch_from_google(code)
            if p:
                display_report(code, p, hi, lo)
            else:
                st.error("❌ حتى جوجل مش عارف يوصل.. السيرفر ده عليه حظر كلي. استخدم اليدوي.")

with tab_manual:
    c1, c2, c3 = st.columns(3)
    pm = c1.number_input("السعر", format="%.2f", key="p3")
    hm = c2.number_input("أعلى", format="%.2f", key="h3")
    lm = c3.number_input("أقل", format="%.2f", key="l3")
    if pm > 0:
        display_report("تحليل يدوي", pm, hm, lm)
