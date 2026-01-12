import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 1. إعداد الصفحة وتنسيق الألوان الناصعة
st.set_page_config(page_title="EGX Ultimate Sniper", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: bold !important; }
    input { background-color: #1e2732 !important; color: #FFFFFF !important; border: 2px solid #3498db !important; }
    div[data-testid="stExpander"] { background-color: #1e2732 !important; border: 1px solid #3498db !important; }
    .stAlert { background-color: #1e2732 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# 2. قاموس الأسماء العربية (كل الأسهم)
EGX_DB = {
    "COMI": "البنك التجاري الدولي", "TMGH": "مجموعة طلعت مصطفى", "FWRY": "فوري",
    "SWDY": "السويدي إليكتريك", "ESRS": "حديد عز", "ABUK": "أبوقير للأسمدة",
    "AMOC": "أمو ك", "BTFH": "بلتون المالية", "SKPC": "سيدي كرير",
    "ATQA": "مصر الوطنية للصلب - عتاقة", "EKHO": "القابضة الكويتية", "ETEL": "المصرية للاتصالات"
}

# 3. دالة جلب السعر اللحظي من جوجل (الأسرع)
def get_live_price(ticker):
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:EGX"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        price = soup.find("div", {"class": "YMlS1d"}).text
        return float(price.replace('EGP', '').replace(',', '').strip())
    except: return None

# 4. واجهة البرنامج
st.title("🏹 رادار قناص البورصة الشامل")
u_input = st.text_input("🔍 ادخل كود السهم (مثلاً TMGH):").upper().strip()

if u_input:
    # محاولة جلب البيانات
    with st.spinner('جاري قنص أحدث البيانات...'):
        p = get_live_price(u_input) # سعر لحظي من جوجل
        
        # جلب البيانات التاريخية من ياهو (عشان السيولة وأعلى/أقل)
        try:
            ticker_ca = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
            stock = yf.Ticker(ticker_ca)
            hist = stock.history(period="1d")
            hi = hist['High'].max() if not hist.empty else p
            lo = hist['Low'].min() if not hist.empty else p
            vol = (hist['Volume'].iloc[-1] * p) / 1e6 if not hist.empty else 0
        except:
            hi, lo, vol = p, p, 0

    if p:
        # حسابات الارتكاز والدعم
        piv = (p + hi + lo) / 3
        s1 = (2 * piv) - hi
        r1 = (2 * piv) - lo
        name = EGX_DB.get(u_input, u_input)

        # --- رادار الإشعارات (الميزة اللي طلبتها) ---
        if p <= (s1 * 1.005):
            st.markdown(f"""
            <div style="background: #2ecc71; padding: 20px; border-radius: 15px; text-align: center; border: 3px solid #ffffff; margin-bottom: 20px;">
                <h1 style="color: #000000 !important; margin: 0;">🔥 فرصة دخول الآن 🔥</h1>
                <p style="color: #000000 !important; font-size: 18px;">السهم {name} وصل منطقة الدعم: {s1:.3f}</p>
            </div>
            """, unsafe_allow_html=True)
        elif p >= (r1 * 0.995):
            st.warning(f"🚀 {name} يقترب من منطقة بيع/اختراق عند {r1:.3f}")

        # --- كارت التحليل الفني الكامل ---
        st.markdown(f"""
        <div style="background: #1e2732; padding: 25px; border-radius: 15px; border: 2px solid #3498db; text-align: center;">
            <h2 style="margin-bottom:20px;">{name}</h2>
            <div style="background: #0d1117; padding: 15px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #f1c40f;">
                <p style="color: #f1c40f !important; margin: 0;">نقطة الارتكاز المحورية</p>
                <h1 style="font-size: 45px; margin: 0;">{piv:.3f}</h1>
            </div>
            
            <div style="display: flex; justify-content: space-between; gap: 10px; margin-bottom: 20px;">
                <div style="flex: 1; background: #0d1117; padding: 15px; border-radius: 10px; border-bottom: 5px solid #e74c3c;">
                    <p style="color: #e74c3c !important; margin: 0;">دخول (د1)</p>
                    <h2 style="margin: 0;">{s1:.3f}</h2>
                </div>
                <div style="flex: 1; background: #0d1117; padding: 15px; border-radius: 10px; border-bottom: 5px solid #2ecc71;">
                    <p style="color: #2ecc71 !important; margin: 0;">بيع (م1)</p>
                    <h2 style="margin: 0;">{r1:.3f}</h2>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-around; font-size: 14px; color: #8b949e;">
                <span>🔝 أعلى: {hi:.3f}</span>
                <span>📉 أدنى: {lo:.3f}</span>
                <span>📊 سيولة: {vol:.1f}M</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # رابط الواتساب
        wa_msg = f"تقرير {name}: السعر {p:.3f} | الدعم {s1:.3f} | الارتكاز {piv:.3f}"
        st.link_button("📲 مشاركة التقرير فورا", f"https://wa.me/?text={urllib.parse.quote(wa_msg)}")
    else:
        st.error("❌ تعذر جلب السعر اللحظي.. تأكد من الكود أو استخدم اليدوي.")

# 5. الإدخال اليدوي الكامل (عشان ميعطلكش لو النت قطع)
st.markdown("---")
with st.expander("🛠️ لوحة التحكم اليدوية (عند الضرورة)"):
    m_p = st.number_input("السعر الآن من الشاشة", format="%.3f")
    m_h = st.number_input("أعلى سعر اليوم", format="%.3f")
    m_l = st.number_input("أقل سعر اليوم", format="%.3f")
    if m_p > 0:
        m_piv = (m_p + m_h + m_l) / 3
        st.success(f"الارتكاز: {m_piv:.3f} | منطقة الدخول: {(2*m_piv)-m_h:.3f}")
