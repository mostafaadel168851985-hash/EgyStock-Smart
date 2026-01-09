import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. إعدادات الواجهة الاحترافية
st.set_page_config(page_title="Pro Stock Analyst", page_icon="💹")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .brand-title { color: #FFFFFF !important; font-family: 'Arial'; font-size: 28px; text-align: center; margin: 10px 0; }
    .telegram-card {
        background: #ffffff; padding: 25px; border-radius: 12px;
        color: #000000 !important; max-width: 450px;
        direction: rtl; text-align: right; margin: auto;
        font-family: 'Segoe UI', sans-serif; box-shadow: 0px 4px 15px rgba(255,255,255,0.1);
    }
    .price-val { font-size: 52px; color: #d32f2f; font-weight: 900; font-family: 'monospace'; line-height: 1; }
    .line { border-top: 1px solid #f0f0f0; margin: 15px 0; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_data_v3(ticker):
    try:
        # تحويل الرمز ليعمل مع ياهو فاينانس (بورصة مصر)
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        
        # سحب بيانات لحظية (فاصل دقيقة واحدة) لضمان أحدث سعر
        df_now = stock.history(period="1d", interval="1m")
        # سحب بيانات تاريخية للتحليل
        df_hist = stock.history(period="30d")
        
        if df_now.empty or df_hist.empty: return None

        # 1. السعر اللحظي (آخر تنفيذة في الدقيقة الحالية)
        current_price = float(df_now['Close'].iloc[-1])
        prev_close = stock.info.get('previousClose', df_hist['Close'].iloc[-2])
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        # 2. تحليل الاتجاه (المتوسطات)
        ma20 = df_hist['Close'].rolling(20).mean().iloc[-1]
        trend = "صاعد 📈" if current_price > ma20 else "هابط 📉"
        
        # 3. حساب السيولة الذكية (مقارنة حجم التداول اللحظي بالمتوسط)
        # Turnover = Price * Volume
        today_volume = df_now['Volume'].sum() # حجم تداول اليوم حتى الآن
        avg_daily_volume = df_hist['Volume'].tail(10).mean()
        
        liq_ratio = today_volume / avg_daily_volume if avg_daily_volume > 0 else 1
        liq_status = "طبيعية ⚖️"
        if liq_ratio > 1.7: liq_status = "انفجارية 🔥🚀"
        elif liq_ratio > 1.2: liq_status = "عالية 🔥"
        
        return {
            "p": current_price, "c": f"{change_pct:+.2f}%",
            "t": trend, "l": liq_status, "v": today_volume * current_price,
            "r": liq_ratio
        }
    except:
        return None

st.markdown('<div class="brand-title">📈 My Smart Stock Helper</div>', unsafe_allow_html=True)
ticker_in = st.text_input("🔍 ادخل الرمز (MOED, ATQA, CRST):", "").strip().upper()

if ticker_in:
    with st.spinner('جاري جلب البيانات من السيرفر العالمي...'):
        data = get_data_v3(ticker_in)
    
    if data:
        p = data['p']
        # حساب الأهداف والدعوم (دقة 3 أرقام عشرية)
        h1, h2 = p * 1.03, p * 1.05
        d1, stop = p * 0.97, p * 0.94
        
        # محرك التوصية
        rec = "مراقبة 🛡️"
        if data['t'] == "صاعد 📈" and data['r'] > 1.1: rec = "شراء / احتفاظ ✅"
        elif data['t'] == "هابط 📉": rec = "خروج / حذر ⚠️"

        st.markdown(f"""
        <div class="telegram-card">
            <b>💎 التقرير الفني لـ {ticker_in}</b>
            <div class="line"></div>
            💰 <b>السعر اللحظي:</b>
            <span class="price-val">{p:.3f}</span>
            📈 <b>التغير:</b> <span style="color:{"green" if "+" in data['c'] else "red"}; font-weight:bold;">{data['c']}</span>
            <div class="line"></div>
            🧭 <b>اتجاه السهم:</b> <b>{data['t']}</b><br>
            💧 <b>نبض السيولة:</b> <b>{data['l']}</b><br>
            💵 <b>قيمة التداول:</b> {data['v']/1_000_000:.2f} مليون ج.م
            <div class="line"></div>
            🚀 <b>الأهداف:</b> {h1:.3f} | {h2:.3f}<br>
            🛡️ <b>الدعم:</b> {d1:.3f} | 🛑 <b>الوقف: {stop:.3f}</b>
            <div class="line"></div>
            📢 <b>التوصية:</b> <span style="font-size: 20px; font-weight: bold; color: #d32f2f;">{rec}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ تعذر الوصول للبيانات. تأكد من الرمز أو حاول مرة أخرى.")
