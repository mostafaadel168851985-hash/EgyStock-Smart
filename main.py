import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 1. إعدادات المظهر (أبيض ناصع)
st.set_page_config(page_title="EGX Sniper Pro v98", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: 900 !important; }
    input { background-color: #1e2732 !important; color: #FFFFFF !important; border: 2px solid #3498db !important; }
</style>
""", unsafe_allow_html=True)

# 2. محرك جلب الداتا المتطور (Anti-Block)
def fetch_data_securely(ticker):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        # محاولة جوجل فاينانس (الأسرع)
        url = f"https://www.google.com/finance/quote/{ticker}:EGX"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_text = soup.find("div", {"class": "YMlS1d"}).text
        price = float(price_text.replace('EGP', '').replace(',', '').strip())
        
        # جلب الهاي واللو من ياهو لتدعيم الداتا
        t_ca = f"{ticker}.CA"
        y_stock = yf.Ticker(t_ca)
        df = y_stock.history(period="1d")
        if not df.empty:
            return price, df['High'].iloc[-1], df['Low'].iloc[-1], df['Volume'].iloc[-1]
        return price, price, price, 0
    except Exception as e:
        return None, None, None, None

# 3. واجهة المستخدم
st.title("🏹 رادار قناص البورصة v98")
st.write("إذا لم تظهر الداتا الآلية، تأكد من كود السهم أو استخدم اليدوي.")

u_input = st.text_input("🔍 ادخل كود السهم (مثلاً TMGH):").upper().strip()

if u_input:
    with st.spinner('⏳ جاري محاولة اختراق الحجب وجلب الداتا...'):
        p, hi, lo, vol = fetch_data_securely(u_input)
    
    if p is not None:
        piv = (p + hi + lo) / 3
        s1 = (2 * piv) - hi
        r1 = (2 * piv) - lo
        
        # --- نظام الإشعارات اللحظي ---
        if p <= (s1 * 1.005):
            st.markdown(f"""
            <div style="background: #2ecc71; padding: 20px; border-radius: 15px; text-align: center; border: 3px solid #ffffff; margin-bottom: 20px;">
                <h1 style="color: #000000 !important; margin: 0;">🔥 إشارة دخول الآن 🔥</h1>
                <p style="color: #000000 !important; font-size: 18px;">السهم عند منطقة دعم قوية: {s1:.3f}</p>
            </div>
            """, unsafe_allow_html=True)

        # عرض كارت التحليل
        st.markdown(f"""
        <div style="background: #1e2732; padding: 25px; border-radius: 20px; border: 2px solid #3498db; text-align: center;">
            <h2 style="color: #ffffff;">تحليل {u_input} اللحظي</h2>
            <div style="background: #0d1117; padding: 15px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #f1c40f;">
                <p style="color: #f1c40f !important; margin: 0;">نقطة الارتكاز</p>
                <h1 style="font-size: 50px; margin: 0;">{piv:.3f}</h1>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 15px;">
                <div style="flex: 1; background: #0d1117; padding: 15px; border-radius: 12px; border-bottom: 6px solid #e74c3c;">
                    <p style="color: #e74c3c !important; margin: 0;">شراء (د1)</p><h2>{s1:.3f}</h2>
                </div>
                <div style="flex: 1; background: #0d1117; padding: 15px; border-radius: 12px; border-bottom: 6px solid #2ecc71;">
                    <p style="color: #2ecc71 !important; margin: 0;">بيع (م1)</p><h2>{r1:.3f}</h2>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ المواقع العالمية تحجب الاتصال الآن. من فضلك استخدم الإدخال اليدوي فوراً.")

# 4. قسم اليدوي الشامل (لا يعتمد على الإنترنت)
st.markdown("---")
with st.expander("🛠️ الإدخال اليدوي (قناص الجلسة)") :
    c1, c2, c3 = st.columns(3)
    mp = c1.number_input("السعر الآن", format="%.3f", key="mp1")
    mh = c2.number_input("أعلى سعر", format="%.3f", key="mh1")
    ml = c3.number_input("أقل سعر", format="%.3f", key="ml1")
    
    if mp > 0:
        mpiv = (mp + mh + ml) / 3
        ms1 = (2 * mpiv) - mh
        st.success(f"الارتكاز: {mpiv:.3f} | الدعم: {ms1:.3f}")
        if mp <= (ms1 * 1.005):
            st.warning("⚠️ تنبيه: السهم يدويًا في منطقة دخول!")
