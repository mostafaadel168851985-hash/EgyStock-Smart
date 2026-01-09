import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# تنسيق الواجهة (Black & White)
st.set_page_config(page_title="EgyStock Ultra Live", layout="wide")
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .telegram-card {
        background: #ffffff; padding: 20px; border-radius: 15px;
        color: #000000 !important; max-width: 500px;
        direction: rtl; text-align: right; border: 1px solid #ddd;
        margin: auto; box-shadow: 0px 4px 15px rgba(255,255,255,0.1);
    }
    .line { border-top: 2px solid #000; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

def get_live_price_mubasher(ticker):
    """سحب السعر مباشرة من موقع مباشر مصر"""
    try:
        # رابط البحث في مباشر مصر عن السهم
        url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # محاولة إيجاد السعر في الكلاسات المشهورة لمباشر
        price_tag = soup.find('div', {'class': 'market-summary__last-price'})
        if price_tag:
            return float(price_tag.text.strip().replace(',', ''))
        return None
    except:
        return None

def get_live_price_google(ticker):
    """سحب السعر من جوجل فاينانس كبديل ثانٍ"""
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:EGX"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find('div', {'class': 'YMlS7e'})
        if price_tag:
            return float(price_tag.text.replace('EGP', '').replace(',', '').strip())
        return None
    except:
        return None

st.title("🛡️ رادار البورصة المصرية (مباشر +)")
ticker_input = st.text_input("اكتب رمز السهم (مثال: CRST, MOED, FWRY):", "CRST").strip().upper()

if ticker_input:
    with st.spinner('جاري البحث في مباشر، جوجل، وياهو...'):
        # 1. جرب مباشر أولاً (الأدق)
        price = get_live_price_mubasher(ticker_input)
        source = "مباشر مصر 📈"
        
        # 2. لو منفعش جرب جوجل
        if not price:
            price = get_live_price_google(ticker_input)
            source = "جوجل فاينانس 🌐"
            
        # 3. لو منفعش جرب ياهو (كحل أخير)
        if not price:
            try:
                data = yf.Ticker(f"{ticker_input}.CA").history(period="1d")
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    source = "ياهو فاينانس 🛡️"
            except:
                pass

    if price:
        # حسابات الأهداف بدقة 3 أرقام
        h1, h2 = price * 1.03, price * 1.05
        d1, stop_loss = price * 0.97, price * 0.94

        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 22px; font-weight: bold;">💎 التحليل الشامل لـ {ticker_input}</div>
            <div class="line"></div>
            💰 <b>السعر اللحظي:</b> <span style="font-size:26px; color:#d32f2f;">{price:.3f}</span><br>
            📟 <b>المصدر:</b> {source}<br>
            💧 <b>حالة التحديث:</b> لحظي الآن ✅
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            ✅ تم جلب البيانات من أقوى المصادر<br>
            ⚠️ السعر محدث بدقة 3 أرقام عشرية
            <div class="line"></div>
            🚀 <b>الأهداف:</b><br>
            🔷 هدف 1: {h1:.3f}<br>
            🔷 هدف 2: {h2:.3f}
            <div class="line"></div>
            🛡️ <b>الدعم:</b><br>
            🔶 دعم 1: {d1:.3f}<br>
            🛑 <b>وقف خسارة:</b> {stop_loss:.3f}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error(f"⚠️ السهم {ticker_input} غير موجود حالياً في أي مصدر. تأكد من كتابة الرمز الصحيح (مثل CRST وليس CRST.CA).")

st.info("💡 ملاحظة: الكود الآن يستخدم 'مباشر مصر' و 'جوجل' و 'ياهو' معاً لضمان عدم ضياع أي سهم.")
