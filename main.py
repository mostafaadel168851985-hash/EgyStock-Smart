import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. إعدادات الصفحة وستايل Thndr X
st.set_page_config(page_title="EgyStock Smart PRO", layout="wide")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .thndr-card {
        background: #0d0d0d; padding: 25px; border-radius: 20px;
        border: 1px dotted #333; color: #ffffff !important;
        max-width: 600px; margin-bottom: 20px;
    }
    .price-tag { font-size: 50px; font-weight: bold; color: #ffffff !important; margin: 10px 0; }
    .label { color: #888; font-size: 14px; text-transform: uppercase; }
    .neon-green { color: #00E676 !important; font-weight: bold; }
    .neon-red { color: #FF3D00 !important; font-weight: bold; }
    .stat-box { background: #1a1a1a; padding: 15px; border-radius: 12px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# اللوجو المودرن
st.markdown('<div style="background:#00E676; color:black; padding:5px 15px; border-radius:10px; display:inline-block; font-weight:bold; font-size:20px;">STX</div> <span style="color:white; font-size:28px; font-weight:bold; margin-left:10px;">EgyStock <span style="color:#00E676">Smart</span></span>', unsafe_allow_html=True)

# المدخلات (دعم للبحث عن CRST)
ticker = st.text_input("🔍 ابحث عن سهم (مثال: CRST, COMI, ATQA):", "CRST").upper().strip()
symbol = f"{ticker}.CA"

def get_full_analysis(sym):
    try:
        # جلب بيانات كافية لحساب المؤشرات (60 يوم)
        data = yf.download(sym, period="2mo", interval="1d", progress=False)
        if data.empty: return None
        
        # حساب RSI (مؤشر القوة)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # حساب السيولة والاتجاه
        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2]
        change = last_close - prev_close
        change_pct = (change / prev_close) * 100
        
        # التوصية الذكية
        if rsi < 30: signal = "شراء قوي 💎"; signal_col = "neon-green"
        elif rsi > 70: signal = "بيع / جني أرباح ⚠️"; signal_col = "neon-red"
        elif change > 0: signal = "احتفاظ / إيجابي ✅"; signal_col = "neon-green"
        else: signal = "مراقبة / حيادي ⚖️"; signal_col = "white"
        
        return {
            "df": data, "price": last_close, "change": change, "pct": change_pct,
            "rsi": rsi, "signal": signal, "signal_col": signal_col,
            "high": data['High'].max(), "low": data['Low'].min(),
            "volume": data['Volume'].iloc[-1]
        }
    except: return None

if ticker:
    analysis = get_full_analysis(symbol)
    
    if analysis:
        # كارت التحليل الكامل (ستايل بوت التليجرام)
        st.markdown(f"""
        <div class="thndr-card">
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size:18px; font-weight:bold;">📊 تحليل سهم: {ticker}</span>
                <span class="neon-green">LIVE</span>
            </div>
            <div class="label" style="margin-top:15px;">السعر الحالي</div>
            <div class="price-tag">{analysis['price']:.2f} <span style="font-size:20px;">EGP</span></div>
            <div class="{'neon-green' if analysis['change'] >= 0 else 'neon-red'}" style="font-size:22px;">
                {analysis['change']:+.2f} ({analysis['pct']:+.2f}%)
            </div>
            
            <hr style="border:0.1px solid #333; margin: 20px 0;">
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="stat-box">
                    <div class="label">التوصية</div>
                    <div class="{analysis['signal_col']}" style="font-size:18px;">{analysis['signal']}</div>
                </div>
                <div class="stat-box">
                    <div class="label">قوة السيولة</div>
                    <div style="color:white; font-size:18px;">{"عالية 🔥" if analysis['rsi'] > 50 else "ضعيفة 🧊"}</div>
                </div>
                <div class="stat-box">
                    <div class="label">أعلى هدف</div>
                    <div class="neon-green" style="font-size:18px;">{analysis['high']:.2f}</div>
                </div>
                <div class="stat-box">
                    <div class="label">وقف الخسارة</div>
                    <div class="neon-red" style="font-size:18px;">{analysis['low']:.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # الشارت الاحترافي
        fig = go.Figure(data=[go.Candlestick(
            x=analysis['df'].index,
            open=analysis['df']['Open'], high=analysis['df']['High'],
            low=analysis['df']['Low'], close=analysis['df']['Close'],
            increasing_line_color='#00E676', decreasing_line_color='#FF3D00'
        )])
        fig.update_layout(template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black', height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"⚠️ السهم {ticker} لم تظهر بياناته بعد. تأكد من الرمز أو حاول لاحقاً (سهم كريستمارك يحتاج أحياناً لوقت للتحديث).")
