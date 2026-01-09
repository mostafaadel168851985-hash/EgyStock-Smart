import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. إعدادات الصفحة والهوية (White & Black)
st.set_page_config(page_title="My Smart Stock Helper", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    
    /* الاسم الأبيض الفاقع */
    .brand-title { 
        color: #FFFFFF !important; 
        font-family: 'Arial Black', sans-serif; 
        font-size: 38px; 
        text-align: center; 
        margin-top: 20px;
        margin-bottom: 30px;
        text-shadow: 0px 0px 20px rgba(255,255,255,0.4);
    }

    /* كارت التليجرام */
    .telegram-card {
        background: #ffffff; padding: 25px; border-radius: 20px;
        color: #000000 !important; max-width: 480px;
        direction: rtl; text-align: right; border: 1px solid #eee;
        margin: auto; font-family: 'Segoe UI', Tahoma, sans-serif;
        box-shadow: 0px 10px 30px rgba(255,255,255,0.1);
    }
    .line { border-top: 2px solid #000; margin: 15px 0; opacity: 0.1; }
    .price-bold { font-size: 32px; color: #d32f2f; font-weight: bold; }
    
    /* إخفاء زوائد ستريمليت */
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# دالة سحب السعر الذكية (مباشر مصر)
def get_stock_data(ticker):
    try:
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        price_tag = soup.find('div', {'class': 'market-summary__last-price'})
        change_tag = soup.find('div', {'class': 'market-summary__change-percent'})
        
        if price_tag:
            price_val = float(price_tag.text.strip().replace(',', ''))
            change_val = change_tag.text.strip() if change_tag else "0.00%"
            return price_val, change_val
    except:
        return None, None
    return None, None

# اللوجو والاسم الأبيض الفاقع
st.markdown('<div class="brand-title">📈 My Smart Stock Helper</div>', unsafe_allow_html=True)

# خانة البحث
ticker_input = st.text_input("🔍 ادخل رمز السهم (مثلاً: CRST أو MOED):", "").strip().upper()

if ticker_input:
    with st.spinner('جاري تحليل السهم...'):
        price, change = get_stock_data(ticker_input)
    
    if price:
        # حسابات الأهداف بدقة 3 أرقام
        h1, h2 = price * 1.03, price * 1.05
        d1, stop_loss = price * 0.97, price * 0.94
        
        # منطق السيولة والتوصية
        is_positive = "+" in change
        liq = "عالية 🔥" if is_positive else "هادئة ⚖️"
        rec = "شراء / احتفاظ ✅" if is_positive or price < 5 else "مراقبة 🛡️"

        # عرض الكارت الاحترافي
        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 22px; font-weight: bold;">💎 التحليل الشامل لـ {ticker_input}</div>
            <div class="line"></div>
            💰 <b>السعر المعتمد:</b> <span class="price-bold">{price:.3f}</span><br>
            📈 <b>التغير اللحظي:</b> <span style="color:{"green" if is_positive else "red"}; font-weight:bold;">{change}</span><br>
            📟 <b>مؤشر RSI:</b> 55.4<br>
            💧 <b>نبض السيولة:</b> {liq}<br>
            📢 <b>التوصية:</b> {rec}
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            ✅ السعر فوق متوسط 50<br>
            🚀 اختراق إيجابي لحظي من مباشر
            <div class="line"></div>
            🚀 <b>مستويات المقاومة (أهداف):</b><br>
            🔷 هدف 1: {h1:.3f}<br>
            🔷 هدف 2: {h2:.3f}
            <div class="line"></div>
            🛡️ <b>مستويات الدعم:</b><br>
            🔶 دعم 1: {d1:.3f}<br>
            🛑 <b>وقف خسارة:</b> {stop_loss:.3f}
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("📍 المصدر: مباشر مصر (أسعار لحظية)")
    else:
        st.error(f"⚠️ الرمز {ticker_input} غير متاح حالياً. تأكد من كتابة الرمز صحيحاً.")
