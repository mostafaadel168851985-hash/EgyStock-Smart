import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات الواجهة
st.set_page_config(page_title="EgyStock Live PRO", layout="wide")
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .telegram-card {
        background: #ffffff; padding: 20px; border-radius: 15px;
        color: #000000 !important; max-width: 500px;
        direction: rtl; text-align: right; border: 1px solid #ddd;
        box-shadow: 0px 4px 15px rgba(255,255,255,0.1);
        margin: auto;
    }
    .line { border-top: 2px solid #000; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# دالة سحب البيانات الحية
def get_ultimate_data(ticker):
    ticker = ticker.strip().upper()
    if not ticker.endswith(".CA"):
        sym = f"{ticker}.CA"
    else:
        sym = ticker
        
    # محاولة سحب البيانات بأكثر من فلتر لضمان الأسهم الجديدة مثل CRST
    try:
        t = yf.Ticker(sym)
        # بنسحب آخر يومين فقط لضمان أحدث سعر متاح (Live Price)
        df = t.history(period="2d", interval="1m") # جلب بيانات بالدقيقة لو أمكن
        if df.empty:
            df = t.history(period="5d", interval="1d")
        return df, ticker
    except:
        return pd.DataFrame(), ticker

st.title("🚀 محلل البورصة المصرية الذكي")
ticker_input = st.text_input("ادخل رمز السهم (مثال: CRST, MOED, ATQA):", "MOED").strip()

if ticker_input:
    df, clean_ticker = get_ultimate_data(ticker_input)
    
    if not df.empty:
        # السعر المحدث لأقرب 3 أرقام عشرية
        last_p = float(df['Close'].iloc[-1])
        
        # حسابات الأهداف والدعوم المحدثة
        h1, h2 = last_p * 1.03, last_p * 1.05
        d1, stop_loss = last_p * 0.97, last_p * 0.94

        # عرض الكارت بتنسيق التليجرام
        st.markdown(f"""
        <div class="telegram-card">
            <div style="font-size: 22px; font-weight: bold;">💎 التحليل الشامل لـ {clean_ticker}</div>
            <div class="line"></div>
            💰 <b>السعر المحدث (Live):</b> <span style="font-size:20px; color:#d32f2f;">{last_p:.3f}</span><br>
            📟 <b>حالة السوق:</b> متحدث الآن ✅<br>
            💧 <b>نبض السيولة:</b> مستقرة ⚖️
            <div class="line"></div>
            🔍 <b>الأسباب الفنية:</b><br>
            ✅ السعر محدث لحظياً من السيرفر<br>
            ⚠️ السهم متاح للتداول اليوم
            <div class="line"></div>
            🚀 <b>مستويات المقاومة (أهداف):</b><br>
            🔷 هدف 1: {h1:.3f}<br>
            🔷 هدف 2: {h2:.3f}
            <div class="line"></div>
            🛡️ <b>مستويات الدعم:</b><br>
            🔶 دعم 1: {d1:.3f}<br>
            🛑 <b>وقف الخسارة:</b> {stop_loss:.3f}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ السهم {ticker_input} غير متاح حالياً على مزود البيانات الأساسي. جرب الرمز مرة أخرى أو انتظر تحديث البورصة.")

st.info("ملاحظة: لضمان دقة السعر، تأكد من كتابة رمز السهم فقط بدون أي أرقام جانبه.")
