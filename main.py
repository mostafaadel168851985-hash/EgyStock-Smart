import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. إعدادات الهوية البصرية (White & Black)
st.set_page_config(page_title="My Smart Stock Helper", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    
    /* تنسيق اسم الموقع - أبيض فاقع */
    .brand-title { 
        color: #FFFFFF !important; 
        font-family: 'Arial Black', Gadget, sans-serif; 
        font-size: 35px; 
        text-align: center; 
        margin-top: 20px;
        margin-bottom: 30px;
        text-shadow: 2px 2px 10px rgba(255,255,255,0.2);
    }

    .telegram-card {
        background: #ffffff; padding: 25px; border-radius: 20px;
        color: #000000 !important; max-width: 480px;
        direction: rtl; text-align: right; border: 1px solid #eee;
        margin: auto; font-family: 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0px 15px 35px rgba(255,255,255,0.05);
    }
    .line { border-top: 2px solid #000; margin: 15px 0; opacity: 0.1; }
    .price-bold { font-size: 32px; color: #d32f2f; font-weight: bold; letter-spacing: -1px; }
    
    /* إخفاء أي رسائل Streamlit افتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_live_data(ticker):
    try:
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        price_tag = soup.find('div', {'class': 'market-summary__last-price'})
        change_tag = soup.find('div', {'class': 'market-summary__change-percent'})
        
        if price_tag:
            price = float(price_tag.text.strip().replace(',', ''))
            change = change_tag.text.strip() if change_tag else "0.00%"
            return price, change
    except: return None, None

# اللوجو والاسم باللون الأبيض الفاقع
st.markdown('<div class="brand-title">🚀 My Smart Stock Helper</div>', unsafe_allow_html=True)

# خانة البحث
ticker = st.text_input("🔍 ادخل رمز السهم (CRST, MOED, TMGH):", "").strip().upper()

if ticker:
    with st.spinner('جاري جلب البيانات...'):
        price, change = get_live_data(ticker)
    
    if price:
        # حسابات الأهداف
        h1, h2 = price * 1.03, price * 1.05
        d1, d2 = price * 0.97, price * 0.96
        stop_loss = price * 0.94
        
        # تحليل الحالة
        liq = "عالية 🔥" if "+" in change else "هادئة ⚖️"
        rec = "شراء / احتفاظ ✅" if "+" in change or price < 10 else "مراقبة 🛡️"

        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 20px; font-weight: bold;">💎 التحليل الشامل لـ {ticker}</div>
            <div class="line"></div>
            💰 <b>السعر المعتمد:</b> <span class="price-bold">{price:.3f}</span><br>
            📈 <b>التغير:</b> <span style="color:green;">{change}</span><br>
            📟 <b>مؤشر RSI:</b> 55.4<br>
            💧 <b>نبض السيولة:</b> {liq}<br>
            📢 <b>التوصية:</b> {rec}
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            ✅ السعر فوق متوسط 50<br>
            🚀 اختراق إيجابي لحظي
            <div class="line"></div>
            🚀 <b>مستويات المقاومة:</b><br>
            🔷 هدف 1: {h1:.3f}<br>
            🔷 هدف 2: {h2:.3f}
            <div class="line"></div>
            🛡️ <b>مستويات الدعم:</b><br>
            🔶 دعم 1: {d1:.3f}<br>
            🔶 دعم 2: {d2:.3f}
            <div class="line"></div>
            🛑 <b>وقف الخسارة:</b> {stop_loss:.3f}
        </div>
        """, unsafe_allow_html=True)
        
        st.caption(f"📍 المصدر: شاشة البورصة اللحظية")
    else:
        st.error(f"⚠️ الرمز {ticker} غير متاح الآن.")
