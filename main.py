import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. إعدادات الصفحة Thndr Style
st.set_page_config(page_title="EgyStock Smart Engine", layout="wide")

st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .thndr-card {
        background: #0d0d0d; padding: 25px; border-radius: 20px;
        border: 1px solid #333; color: white !important;
        max-width: 600px; margin-bottom: 20px;
    }
    .price-huge { font-size: 50px; font-weight: bold; margin: 10px 0; }
    .neon-green { color: #00E676 !important; font-weight: bold; }
    .neon-red { color: #FF3D00 !important; font-weight: bold; }
    .label-gray { color: #888; font-size: 14px; }
    hr { border: 0.1px solid #333; margin: 20px 0; }
    .signal-box { background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #00E676; }
    </style>
    """, unsafe_allow_html=True)

# اللوجو
st.markdown('<div style="background:#00E676; color:black; padding:5px 15px; border-radius:10px; display:inline-block; font-weight:bold;">STX</div> <span style="color:white; font-size:25px; font-weight:bold; margin-left:10px;">EgyStock <span style="color:#00E676">Smart</span></span>', unsafe_allow_html=True)

# مدخل البحث الشامل
ticker_input = st.text_input("🔍 اكتب رمز أي سهم (مثال: TMGH, FWRY, COMI, ORAS):", "TMGH").upper().strip()

def fix_symbol(s):
    if not s.endswith(".CA"): return f"{s}.CA"
    return s

if ticker_input:
    symbol = fix_symbol(ticker_input)
    
    try:
        # جلب البيانات بطريقة مستقرة جداً
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        
        if not df.empty and len(df) > 5:
            # تنظيف البيانات لضمان عدم حدوث Error (تحويلها لأرقام بسيطة)
            last_p = float(df['Close'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2])
            change = last_p - prev_p
            pct = (change / prev_p) * 100
            
            # حساب RSI (السيولة)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_val = float(100 - (100 / (1 + rs.iloc[-1])))

            # التحليل الفني الذكي (التوصية)
            avg_20 = float(df['Close'].rolling(20).mean().iloc[-1])
            liquidity = "عالية 🔥" if rsi_val > 50 else "ضعيفة 🧊"
            
            if rsi_val < 35: status = "شراء (منطقة دعم) 💎"; col = "neon-green"
            elif rsi_val > 75: status = "بيع (منطقة جني أرباح) ⚠️"; col = "neon-red"
            else: status = "احتفاظ / مراقبة ⚖️"; col = "white"

            # عرض الكارت الاحترافي (زي بوت التليجرام بالظبط)
            st.markdown(f"""
            <div class="thndr-card">
                <div style="font-size: 22px; font-weight: bold;">💎 التحليل الشامل لـ {ticker_input}</div>
                <hr>
                <div class="label-gray">السعر الحالي</div>
                <div class="price-huge">{last_p:.2f} <span style="font-size:20px;">EGP</span></div>
                <div class="{'neon-green' if change >= 0 else 'neon-red'}" style="font-size:22px;">
                    {change:+.2f} ({pct:+.2f}%) {'▲' if change >= 0 else '▼'}
                </div>
                <hr>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div><span class="label-gray">مؤشر RSI</span><br><b>{rsi_val:.1f}</b></div>
                    <div><span class="label-gray">نبض السيولة</span><br><b>{liquidity}</b></div>
                    <div><span class="label-gray">المقاومة (أعلى)</span><br><b class="neon-green">{float(df['High'].max()):.2f}</b></div>
                    <div><span class="label-gray">الدعم (أقل)</span><br><b class="neon-red">{float(df['Low'].min()):.2f}</b></div>
                </div>
                <div class="signal-box">
                    <span class="label-gray">التوصية الفنية:</span><br>
                    <b style="color:{col}; font-size:18px;">{status}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # الشارت
            
            fig = go.Figure(data=[go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                increasing_line_color='#00E676', decreasing_line_color='#FF3D00'
            )])
            fig.update_layout(template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black', height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning(f"⚠️ لا توجد بيانات كافية حالياً لرمز {ticker_input}. تأكد من صحة الرمز من موقع البورصة.")
            
    except Exception as e:
        st.error("سيرفر البيانات لا يستجيب، حاول مرة أخرى خلال ثوانٍ.")
