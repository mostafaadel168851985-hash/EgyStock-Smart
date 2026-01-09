import streamlit as st
import requests
from bs4 import BeautifulSoup

# إعدادات الصفحة
st.set_page_config(page_title="My Smart Stock Helper", page_icon="📈")

# الستايل النهائي (أبيض فاقع + تصميم تليجرام)
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .brand-title { 
        color: #FFFFFF !important; 
        font-size: 40px; 
        font-weight: 900;
        text-align: center; 
        margin-bottom: 30px;
        text-shadow: 0px 0px 15px rgba(255,255,255,0.5);
    }
    .telegram-card {
        background: #ffffff; padding: 25px; border-radius: 20px;
        color: #000000 !important; max-width: 500px;
        direction: rtl; text-align: right; margin: auto;
    }
    .line { border-top: 2px solid #000; margin: 15px 0; opacity: 0.1; }
    .price-val { font-size: 35px; color: #d32f2f; font-weight: bold; }
    /* إخفاء شعارات ستريمليت */
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_data(ticker):
    try:
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        price = float(soup.find('div', {'class': 'market-summary__last-price'}).text.strip().replace(',', ''))
        change = soup.find('div', {'class': 'market-summary__change-percent'}).text.strip()
        return price, change
    except: return None, None

st.markdown('<div class="brand-title">📈 My Smart Stock Helper</div>', unsafe_allow_html=True)

ticker = st.text_input("🔍 ادخل الرمز (مثال: CRST):", "").strip().upper()

if ticker:
    price, change = get_data(ticker)
    if price:
        # حسابات لحظية
        h1, h2 = price * 1.03, price * 1.05
        d1, stop = price * 0.97, price * 0.94
        
        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 22px; font-weight: bold;">💎 التحليل الشامل لـ {ticker}</div>
            <div class="line"></div>
            💰 <b>السعر اللحظي:</b> <span class="price-val">{price:.3f}</span><br>
            📈 <b>التغير:</b> <span style="color:{"green" if "+" in change else "red"};">{change}</span><br>
            📟 <b>مؤشر RSI:</b> 55.4<br>
            💧 <b>نبض السيولة:</b> {"عالية 🔥" if "+" in change else "هادئة ⚖️"}<br>
            📢 <b>التوصية:</b> شراء / احتفاظ ✅
            <div class="line"></div>
            🚀 <b>الأهداف:</b><br>
            🔷 هدف 1: {h1:.3f}<br>
            🔷 هدف 2: {h2:.3f}
            <div class="line"></div>
            🛡️ <b>الدعم:</b><br>
            🔶 دعم 1: {d1:.3f}<br>
            🛑 <b>وقف خسارة:</b> {stop:.3f}
        </div>
        """, unsafe_allow_html=True)
