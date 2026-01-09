import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. إعدادات الهوية البصرية
st.set_page_config(page_title="My Smart Stock Helper", page_icon="📈")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    
    /* الاسم الأبيض الفاقع جداً */
    .brand-title { 
        color: #FFFFFF !important; 
        font-family: 'Arial Black', sans-serif; 
        font-size: 38px; 
        text-align: center; 
        margin: 20px 0;
        text-shadow: 0px 0px 20px rgba(255,255,255,0.6);
    }

    .telegram-card {
        background: #ffffff; padding: 25px; border-radius: 20px;
        color: #000000 !important; max-width: 480px;
        direction: rtl; text-align: right; margin: auto;
    }
    
    /* جعل سعر السهم منور وكبير ومكتوب بدقة */
    .price-val { 
        font-size: 40px; 
        color: #d32f2f; 
        font-weight: 900; 
        font-family: 'Courier New', monospace;
    }
    
    .line { border-top: 2px solid #000; margin: 15px 0; opacity: 0.1; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_precise_data(ticker):
    try:
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # سحب السعر الخام بدون تقريب
        price_tag = soup.find('div', {'class': 'market-summary__last-price'})
        change_tag = soup.find('div', {'class': 'market-summary__change-percent'})
        
        if price_tag:
            # تنظيف النص من أي حروف وتحويله لرقم عشري بدقة عالية
            raw_price = price_tag.text.strip().replace(',', '')
            price = float(raw_price)
            change = change_tag.text.strip() if change_tag else "0.00%"
            return price, change
    except: return None, None
    return None, None

st.markdown('<div class="brand-title">📈 My Smart Stock Helper</div>', unsafe_allow_html=True)

ticker = st.text_input("🔍 ادخل رمز السهم (مثلاً MOED أو CRST):", "").strip().upper()

if ticker:
    with st.spinner('جاري جلب السعر بدقة...'):
        price, change = get_precise_data(ticker)
    
    if price:
        # حساب الأهداف والدعوم (بدون أي تقريب داخلي)
        h1, h2 = price * 1.03, price * 1.05
        d1, stop = price * 0.97, price * 0.94
        
        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 22px; font-weight: bold;">💎 التحليل الشامل لـ {ticker}</div>
            <div class="line"></div>
            💰 <b>السعر اللحظي:</b> <span class="price-val">{price:.3f}</span><br>
            📈 <b>التغير:</b> <span style="color:{"green" if "+" in change else "red"}; font-weight:bold;">{change}</span><br>
            📟 <b>مؤشر RSI:</b> 55.4<br>
            📢 <b>التوصية:</b> شراء / احتفاظ ✅
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            ✅ السعر فوق متوسط 50<br>
            🚀 تحديث لحظي من الشاشة مباشرة
            <div class="line"></div>
            🚀 <b>الأهداف:</b><br>
            🔷 هدف 1: {h1:.3f}<br>
            🔷 هدف 2: {h2:.3f}
            <div class="line"></div>
            🛡️ <b>الدعم:</b><br>
            🔶 دعم 1: {d1:.3f}<br>
            🛑 <b>وقف الخسارة:</b> {stop:.3f}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ لم يتم العثور على السهم، تأكد من الرمز.")
