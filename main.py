import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta  # مكتبة التحليل الفني

# 1. إعدادات الواجهة الاحترافية
st.set_page_config(page_title="EGX Alpha Analyst", page_icon="🚀")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .brand-title { color: #FFFFFF !important; font-family: 'Arial'; font-size: 28px; text-align: center; margin: 10px 0; }
    .telegram-card {
        background: #ffffff; padding: 25px; border-radius: 15px;
        color: #000000 !important; max-width: 450px;
        direction: rtl; text-align: right; margin: auto;
        font-family: 'Segoe UI', sans-serif; border-right: 8px solid #d32f2f;
    }
    .price-val { font-size: 55px; color: #d32f2f; font-weight: 900; font-family: 'monospace'; line-height: 1; }
    .status-box { padding: 5px 10px; border-radius: 5px; font-weight: bold; display: inline-block; }
    .line { border-top: 1px solid #f0f0f0; margin: 15px 0; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# القاموس الذكي للرموز
SYMBOLS_MAP = {
    "CRST": "UEGC", 
    "KMT": "UEGC",
    "MOED": "MOED",
    "ATQA": "ATQA",
    "TMGH": "TMGH"
}

def get_pro_analysis(ticker):
    try:
        raw_ticker = ticker.upper().strip()
        fixed_ticker = SYMBOLS_MAP.get(raw_ticker, raw_ticker)
        symbol = f"{fixed_ticker}.CA"
        
        stock = yf.Ticker(symbol)
        df = stock.history(period="60d", interval="1d") # سحب داتا كافية للـ RSI
        df_now = stock.history(period="1d", interval="1m")
        
        if df.empty or df_now.empty: return None

        # حساب السعر الحالي بدقة
        current_p = float(df_now['Close'].iloc[-1])
        
        # حساب RSI (14)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        rsi_val = df['RSI'].iloc[-1]
        
        # حساب المتوسطات
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        
        # حساب السيولة
        today_vol = df_now['Volume'].sum()
        avg_vol = df['Volume'].tail(10).mean()
        liq_ratio = today_vol / avg_vol if avg_vol > 0 else 1
        
        return {
            "p": current_p,
            "rsi": rsi_val,
            "t": "صاعد 📈" if current_p > ma20 else "هابط 📉",
            "r": liq_ratio,
            "v": today_vol * current_p,
            "prev": stock.info.get('previousClose', df['Close'].iloc[-2])
        }
    except: return None

st.markdown('<div class="brand-title">💎 EGX Pro Live Scanner</div>', unsafe_allow_html=True)
ticker_in = st.text_input("🔍 ادخل الرمز (MOED, CRST, ATQA):", "").strip().upper()

if ticker_in:
    with st.spinner('جاري المسح الفني الشامل...'):
        data = get_pro_analysis(ticker_in)
    
    if data:
        p = data['p']
        rsi = data['rsi']
        change = ((p - data['prev']) / data['prev']) * 100
        
        # منطق التوصية المتقدم
        rec = "مراقبة 🛡️"
        color = "#000000" # أسود عادي
        
        if p > (p * 0.97) and rsi < 35: 
            rec = "فرصة شراء (قاع) 🚀"
            color = "#2e7d32" # أخضر
        elif data['t'] == "صاعد 📈" and data['r'] > 1.2:
            rec = "احتفاظ - سيولة قوية ✅"
            color = "#1565c0" # أزرق
        elif rsi > 75:
            rec = "جني أرباح (متشبع) ⚠️"
            color = "#ef6c00" # برتقالي
        elif p < (p * 0.94):
            rec = "خروج - كسر دعم 🛑"
            color = "#d32f2f" # أحمر

        st.markdown(f"""
        <div class="telegram-card" style="border-right-color: {color};">
            <b>📊 تقرير الأداء لـ {ticker_in}</b>
            <div class="line"></div>
            💰 <b>السعر اللحظي:</b>
            <span class="price-val">{p:.3f}</span>
            📈 <b>التغير:</b> <span style="color:{"green" if change > 0 else "red"}; font-weight:bold;">{change:+.2f}%</span>
            <div class="line"></div>
            📉 <b>مؤشر القوة (RSI):</b> <b>{rsi:.1f}</b> {"(منطقة شراء)" if rsi < 30 else "(منطقة بيع)" if rsi > 70 else "(منطقة آمنة)"}<br>
            🧭 <b>الاتجاه:</b> <b>{data['t']}</b><br>
            💧 <b>السيولة:</b> <b>{"عالية 🔥" if data['r'] > 1.3 else "هادئة ⚖️"}</b>
            <div class="line"></div>
            🚀 <b>أهدافك:</b> {(p*1.03):.3f} | {(p*1.05):.3f}<br>
            🛑 <b>وقف الخسارة: {(p*0.95):.3f}</b>
            <div class="line"></div>
            📢 <b>التوصية:</b> <span style="font-size: 22px; font-weight: bold; color: {color};">{rec}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ فشل في جلب البيانات، تأكد من الرمز.")
