import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 1. إعدادات الصفحة والألوان (أبيض ناصع وخطوط واضحة)
st.set_page_config(page_title="EGX Sniper Elite v96", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: 900 !important; }
    input { background-color: #1e2732 !important; color: #FFFFFF !important; border: 2px solid #3498db !important; }
    div[data-testid="stExpander"] { background-color: #1e2732 !important; border: 1px solid #3498db !important; }
</style>
""", unsafe_allow_html=True)

# 2. القاموس الكامل لأسماء الأسهم العربية
EGX_DB = {
    "COMI": "البنك التجاري الدولي", "TMGH": "مجموعة طلعت مصطفى", "FWRY": "فوري",
    "SWDY": "السويدي إليكتريك", "ESRS": "حديد عز", "ABUK": "أبوقير للأسمدة",
    "AMOC": "أمو ك", "BTFH": "بلتون المالية", "SKPC": "سيدي كرير",
    "ATQA": "مصر الوطنية للصلب - عتاقة", "EKHO": "القابضة الكويتية", "ETEL": "المصرية للاتصالات"
}

# 3. محرك جلب البيانات الذكي (Multi-Source)
def get_stock_data(ticker):
    # محاولة أولى: Google Finance (الأسرع)
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:EGX"
        soup = BeautifulSoup(requests.get(url, timeout=5).text, 'html.parser')
        price = float(soup.find("div", {"class": "YMlS1d"}).text.replace('EGP', '').replace(',', '').strip())
        # جلب الهاي واللو التقريبي من ياهو لتدعيم البيانات
        t_ca = f"{ticker}.CA"
        y_data = yf.download(t_ca, period="1d", progress=False)
        hi = y_data['High'].iloc[-1] if not y_data.empty else price
        lo = y_data['Low'].iloc[-1] if not y_data.empty else price
        return price, hi, lo
    except:
        # محاولة ثانية: Yahoo Finance مباشرة
        try:
            t_ca = f"{ticker}.CA"
            y_data = yf.download(t_ca, period="1d", progress=False)
            if not y_data.empty:
                return y_data['Close'].iloc[-1], y_data['High'].iloc[-1], y_data['Low'].iloc[-1]
        except: return None, None, None

# 4. واجهة البرنامج الأساسية
st.title("🏹 قناص البورصة - التحليل الآلي v96")

u_input = st.text_input("🔍 ادخل كود السهم (مثلاً TMGH):").upper().strip()

if u_input:
    p, hi, lo = get_stock_data(u_input)
    
    if p:
        # الحسابات الفنية (الارتكاز والدعم والمقاومة)
        piv = (p + hi + lo) / 3
        s1 = (2 * piv) - hi
        r1 = (2 * piv) - lo
        name = EGX_DB.get(u_input, u_input)

        # --- [الإضافة الجديدة] نظام إشعارات حالة السعر ---
        if p <= (s1 * 1.005):
            st.markdown(f"""
            <div style="background: #2ecc71; padding: 20px; border-radius: 15px; text-align: center; border: 3px solid #ffffff; margin-bottom: 20px;">
                <h1 style="color: #000000 !important; margin: 0;">🔥 إشارة دخول (عند الدعم) 🔥</h1>
                <p style="color: #000000 !important; font-size: 18px;">السعر الحالي {p:.3f} مناسب جداً للشراء</p>
            </div>
            """, unsafe_allow_html=True)
        elif p >= (r1 * 0.995):
            st.markdown(f"""
            <div style="background: #e74c3c; padding: 20px; border-radius: 15px; text-align: center; border: 3px solid #ffffff; margin-bottom: 20px;">
                <h1 style="color: #ffffff !important; margin: 0;">🚀 إشارة بيع (عند المقاومة) 🚀</h1>
                <p style="color: #ffffff !important; font-size: 18px;">السهم وصل لمستهدف البيع اللحظي</p>
            </div>
            """, unsafe_allow_html=True)

        # --- كارت التحليل الفني الشامل ---
        st.markdown(f"""
        <div style="background: #1e2732; padding: 25px; border-radius: 20px; border: 2px solid #3498db; text-align: center;">
            <h2 style="color: #ffffff; margin-bottom: 10px;">{name}</h2>
            <div style="background: #0d1117; padding: 15px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #f1c40f;">
                <p style="color: #f1c40f !important; margin: 0;">نقطة الارتكاز (الميزان)</p>
                <h1 style="font-size: 50px; margin: 0; color: #ffffff;">{piv:.3f}</h1>
            </div>
            
            <div style="display: flex; justify-content: space-between; gap: 15px;">
                <div style="flex: 1; background: #0d1117; padding: 15px; border-radius: 12px; border-bottom: 6px solid #e74c3c;">
                    <p style="color: #e74c3c !important; margin: 0;">منطقة الشراء (د1)</p>
                    <h2 style="margin: 5px 0;">{s1:.3f}</h2>
                </div>
                <div style="flex: 1; background: #0d1117; padding: 15px; border-radius: 12px; border-bottom: 6px solid #2ecc71;">
                    <p style="color: #2ecc71 !important; margin: 0;">منطقة البيع (م1)</p>
                    <h2 style="margin: 5px 0;">{r1:.3f}</h2>
                </div>
            </div>
            
            <div style="margin-top: 20px; color: #8b949e; font-size: 14px; display: flex; justify-content: space-around;">
                <span>السعر الآن: {p:.3f}</span>
                <span>أعلى: {hi:.3f}</span>
                <span>أدنى: {lo:.3f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # زر الواتساب
        wa_msg = f"تحليل {name}:\nالسعر: {p:.3f}\nالارتكاز: {piv:.3f}\nشراء: {s1:.3f}\nبيع: {r1:.3f}"
        st.link_button("📲 إرسال التقرير عبر واتساب", f"https://wa.me/?text={urllib.parse.quote(wa_msg)}")
    else:
        st.error("❌ عذراً، تعذر جلب البيانات آلياً الآن. برجاء استخدام الإدخال اليدوي بالأسفل.")

# 5. الإدخال اليدوي (كامل التفاصيل)
st.markdown("---")
with st.expander("🛠️ الإدخال اليدوي (إذا توقفت البيانات الآلية)"):
    m_p = st.number_input("السعر الحالي", format="%.3f", key="man_p")
    m_h = st.number_input("أعلى سعر", format="%.3f", key="man_h")
    m_l = st.number_input("أقل سعر", format="%.3f", key="man_l")
    
    if m_p > 0 and m_h > 0:
        m_piv = (m_p + m_h + m_l) / 3
        st.markdown(f"""
        <div style="background: #1e2732; padding: 15px; border-radius: 10px; border: 1px dashed #f1c40f; text-align: center;">
            <p style="color: #f1c40f;">نتائج الإدخال اليدوي:</p>
            <h3>الارتكاز: {m_piv:.3f} | الدعم: {(2*m_piv)-m_h:.3f} | المقاومة: {(2*m_piv)-m_l:.3f}</h3>
        </div>
        """, unsafe_allow_html=True)
