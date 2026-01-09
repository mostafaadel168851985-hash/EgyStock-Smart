import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعداد الصفحة
st.set_page_config(page_title="EGX Sniper Elite", page_icon="⚡", layout="centered")

# --- CSS التنسيق العصري ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    
    /* الكارت الأبيض الاحترافي */
    .report-card { 
        background: white; padding: 25px; border-radius: 20px; 
        color: black; direction: rtl; text-align: right; 
        margin-bottom: 20px; border-right: 10px solid #1a73e8;
        box-shadow: 0 10px 20px rgba(255,255,255,0.1);
    }
    
    .price-tag { font-size: 55px; color: #d32f2f; font-weight: 900; font-family: 'Courier New'; line-height: 1; }
    
    /* عناوين الإدخال اليدوي المضيئة */
    label { color: #00d4ff !important; font-size: 18px !important; font-weight: bold !important; }

    /* زر الواتساب الـ Modern و الـ Active */
    .wa-btn {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; padding: 18px; border-radius: 50px;
        text-align: center; font-weight: 900; font-size: 20px;
        display: block; text-decoration: none; margin: 20px 0;
        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
        transition: all 0.3s ease;
        animation: pulse-green 2s infinite;
    }
    .wa-btn:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(37, 211, 102, 0.6); }
    
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(37, 211, 102, 0); }
        100% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }
    }

    .trend-tag { padding: 4px 10px; border-radius: 8px; font-weight: bold; color: white; }
    .up { background-color: #2e7d32; }
    .down { background-color: #c62828; }
    </style>
    """, unsafe_allow_html=True)

# --- وظيفة التحليل الذكي للاتجاهات ---
def get_detailed_analysis(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        df = stock.history(period="200d")
        if df.empty: return None
        
        p = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        
        # حساب الاتجاهات بذكاء
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma100 = df['Close'].rolling(100).mean().iloc[-1]
        
        t_short = "صاعد 🟢" if p > ma20 else "هابط 🔴"
        t_mid = "صاعد 🟢" if p > ma50 else "هابط 🔴"
        t_long = "صاعد 🟢" if p > ma100 else "هابط 🔴"
        
        # قوة التوصية
        score = sum([p > ma20, p > ma50, p > ma100])
        advice = "دخول قوي 🔥" if score == 3 else "احتفاظ / مراقبة ⚖️" if score >= 1 else "خروج / حذر 🛑"
        
        return {
            "p": p, "prev": prev, "rsi": rsi, 
            "vol": (df['Volume'].iloc[-1]*p)/1_000_000,
            "ts": t_short, "tm": t_mid, "tl": t_long, "adv": advice
        }
    except: return None

# --- الواجهة ---
st.markdown("<h1 style='text-align:center; color:white;'>⚡ EGX Sniper Elite v7</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 رمز السهم (مثال: TMGH):", "").strip().upper()

if u_input:
    data = get_detailed_analysis(u_input)
    msg = ""

    if data:
        p = data['p']
        chg = ((p - data['prev']) / data['prev']) * 100
        st.markdown(f"""
        <div class="report-card">
            <h2 style="margin:0;">💎 تحليل {u_input} الاحترافي</h2>
            <div class="price-tag">{p:.3f}</div>
            <b style="color:{'green' if chg > 0 else 'red'}; font-size:22px;">{chg:+.2f}%</b>
            <p>RSI: {data['rsi']:.1f} | السيولة: {data['vol']:.2f}M</p>
            <hr>
            <h4 style="margin-bottom:10px;">🧭 بوصلة الاتجاهات:</h4>
            • المدى القصير: <b>{data['ts']}</b><br>
            • المدى المتوسط: <b>{data['tm']}</b><br>
            • المدى الطويل: <b>{data['tl']}</b><br>
            <hr>
            <b>📢 التوصية النهائية:</b> <span style="font-size:18px; color:#1a73e8;">{data['adv']}</span>
            <hr>
            <b>🚀 الأهداف:</b> {p*1.03:.3f} | {p*1.06:.3f} | <b>🛑 الوقف:</b> {p*0.94:.3f}
        </div>
        """, unsafe_allow_html=True)
        msg = f"⚡ قناص البورصة - {u_input}:\n💰 السعر: {p:.3f}\n🧭 قصير: {data['ts']}\n🧭 متوسط: {data['tm']}\n🧭 طويل: {data['tl']}\n📢 التوصية: {data['adv']}\n🚀 الأهداف: {p*1.03:.3f} - {p*1.06:.3f}"

    # لوحة التحليل اليدوي
    st.markdown(f'<div style="background:white; color:black; padding:10px; border-radius:10px; text-align:center; font-weight:bold; margin:20px 0;">🛠️ لوحة الإدخال اليدوي المتقدمة</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: m_p = st.number_input("💵 السعر الآن:", format="%.3f")
    with c2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f")
    with c3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f")

    if m_p > 0:
        pivot = (m_h + m_l + m_p) / 3
        r1 = (2 * pivot) - m_l
        msg = f"🛠️ تحليل يديوي {u_input}:\n💰 السعر: {m_p:.3f}\n🎯 الهدف: {r1:.3f}\n📍 الارتكاز: {pivot:.3f}"

    if msg:
        st.write("---")
        # زر الواتساب الجديد
        wa_url = f"https://wa.me/?text={msg.replace(' ', '%20').replace('', '%0A')}"
        st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-btn">🚀 إرسال التقرير للواتساب الآن</a>', unsafe_allow_html=True)
        st.info("💡 النص جاهز.. الزر سيفتح واتساب مباشرة")

st.caption("EGX Sniper v7.0 | Advanced Analytics Edition")
