import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# إعدادات الستايل (أبيض ناصع)
st.set_page_config(page_title="EgyStock PRO", layout="wide")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .white-card {
        background: #111111; padding: 20px; border-radius: 15px;
        border: 1px solid #333; color: #ffffff !important;
    }
    .price { font-size: 45px; font-weight: bold; color: #ffffff !important; }
    .up { color: #00E676 !important; }
    .down { color: #FF3D00 !important; }
    </style>
    """, unsafe_allow_html=True)

# اللوجو السمارت
st.markdown('<div style="background:#00E676; color:black; padding:5px 15px; border-radius:10px; display:inline-block; font-weight:bold;">STX</div> <span style="color:white; font-size:25px; font-weight:bold;"> EgyStock Smart</span>', unsafe_allow_html=True)

ticker = st.text_input("بحث عن سهم (مثلاً: COMI, ATQA, CRST):", "COMI").upper()
symbol = f"{ticker}.CA"

# محرك جلب البيانات "الفولاذي"
def get_data(sym):
    try:
        # المحاولة الأولى: ياهو فاينانس بأحدث طريقة
        d = yf.download(sym, period="1mo", interval="1d", progress=False, timeout=10)
        if d.empty:
            # المحاولة الثانية: لو ياهو معلق، نجرب نسحب بصيغة تانية
            t = yf.Ticker(sym)
            d = t.history(period="1mo")
        return d
    except:
        return pd.DataFrame()

if st.button("تحليل الآن"):
    data = get_data(symbol)
    
    if not data.empty:
        last_p = data['Close'].iloc[-1]
        prev_p = data['Close'].iloc[-2]
        change = last_p - prev_p
        
        # كارت التحليل الأبيض
        st.markdown(f"""
        <div class="white-card">
            <h2 style="color:white;">{ticker} - البورصة المصرية</h2>
            <div class="price">{last_p:.2f} EGP</div>
            <div class="{'up' if change >= 0 else 'down'}" style="font-size:22px;">
                {change:+.2f} ({ (change/prev_p)*100 :+.2f}%)
            </div>
            <hr style="border:0.1px solid #444;">
            <div style="display: flex; justify-content: space-between; font-size:18px;">
                <span>المقاومة: <b class="up">{data['High'].max():.2f}</b></span>
                <span>الدعم: <b class="down">{data['Low'].min():.2f}</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # الشارت
        fig = go.Figure(data=[go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'],
            increasing_line_color='#00E676', decreasing_line_color='#FF3D00'
        )])
        fig.update_layout(template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black', height=450, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("⚠️ ياهو فاينانس لا يستجيب حالياً لهذا السهم. جرب رمزاً آخر أو انتظر دقيقة.")
