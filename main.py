import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعداد الصفحة
st.set_page_config(page_title="EGX Sniper Professional", layout="centered")

# --- CSS لتصميم الكارت المطابق للمعلومات والشكل ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    
    .whatsapp-card {
        background-color: #1e2732; 
        color: white; 
        padding: 25px; 
        border-radius: 15px; 
        direction: rtl; 
        text-align: right;
        font-family: 'Arial', sans-serif;
        border: 1px solid #333;
        line-height: 1.6;
    }
    .card-header { font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 5px; color: #ffffff; }
    .separator { border-top: 1px solid #555; margin: 10px 0; width: 100%; }
    .price-big { font-size: 40px; color: #ff3b30; font-weight: bold; font-family: monospace; display: block; text-align: center; }
    .info-row { font-size: 16px; margin: 8px 0; }
    .label-blue { color: #3498db; font-weight: bold; }
    
    /* إبراز عناوين الإدخال */
    label { color: #ffffff !important; font-weight: bold !important; font-size: 16px !important; }
    
    .wa-btn-active {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; padding: 15px; border-radius: 50px;
        text-align: center; font-weight: bold; text-decoration: none;
        display: block; margin: 20px 0; animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(37, 211, 102, 0); }
        100% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

def get_full_data(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        df = stock.history(period="150d")
        if df.empty: return None
        
        p = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        
        # الاتجاهات بناءً على المتوسطات
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma100 = df['Close'].rolling(100).mean().iloc[-1]
        
        ts = "صاعد 🟢" if p > ma20 else "هابط 🔴"
        tm = "صاعد 🟢" if p > ma50 else "هابط 🔴"
        tl = "صاعد 🟢" if p > ma100 else "هابط 🔴"
        
        # التوصية
        score = sum([p > ma20, p > ma50, p > ma100])
        adv = "دخول قوي 🔥" if score == 3 else "احتفاظ / مراقبة ⚖️" if score >= 1 else "خروج / حذر 🛑"
        
        return {
            "p": p, "prev": prev, "rsi": rsi, 
            "vol": (df['Volume'].iloc[-1]*p)/1_000_000,
            "ts": ts, "tm": tm, "tl": tl, "adv": adv
        }
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 قناص البورصة المصرية</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثل ATQA, MOED, CRST):", "").upper()

if u_input:
    d = get_full_data(u_input)
    report_msg = ""

    if d:
        p = d['p']
        chg = ((p - d['prev']) / d['prev']) * 100
        # الكارت المتكامل (شكل + معلومات)
        st.markdown(f"""
        <div class="whatsapp-card">
            <div class="card-header">💎 التحليل الشامل لـ {u_input}</div>
            <div class="separator"></div>
            <div class="price-big">{p:.3f}</div>
            <div style="text-align:center; color:{'#4cd964' if chg > 0 else '#ff3b30'}; font-weight:bold;">{chg:+.2f}%</div>
            
            <div class="info-row">📟 مؤشر RSI: <b>{d['rsi']:.1f}</b></div>
            <div class="info-row">💧 نبض السيولة: <b>{'عالية 🔥' if d['vol'] > 5 else 'هادئة ⚖️'} ({d['vol']:.1f}M)</b></div>
            <div class="info-row">📢 التوصية: <b>{d['adv']}</b></div>
            
            <div class="separator"></div>
            <div class="info-row"><span class="label-blue">🔍 بوصلة الاتجاهات:</span></div>
            <div class="info-row">• مدى قصير: <b>{d['ts']}</b></div>
            <div class="info-row">• مدى متوسط: <b>{d['tm']}</b></div>
            <div class="info-row">• مدى طويل: <b>{d['tl']}</b></div>
            
            <div class="separator"></div>
            <div class="info-row"><span class="label-blue">🚀 مستويات المقاومة:</span></div>
            <div class="info-row">🔹 هدف 1: <b>{p*1.025:.3f}</b></div>
            <div class="info-row">🔹 هدف 2: <b>{p*1.050:.3f}</b></div>
            
            <div class="separator"></div>
            <div class="info-row"><span class="label-blue">🛡️ مستويات الدعم:</span></div>
            <div class="info-row">🔸 دعم 1: <b>{p*0.975:.3f}</b></div>
            <div class="info-row">🔸 دعم 2: <b>{p*0.950:.3f}</b></div>
            
            <div class="separator"></div>
            <div class="info-row">🛑 وقف الخسارة: <b>{p*0.940:.3f}</b></div>
        </div>
        """, unsafe_allow_html=True)
        report_msg = f"💎 تحليل {u_input}\n💰 السعر: {p:.3f}\n🧭 الاتجاه: {d['ts']}\n🚀 أهداف: {p*1.025:.3f} - {p*1.050:.3f}\n🛑 وقف: {p*0.940:.3f}"

    # --- لوحة التحليل اليدوي المزدوج (بارزة) ---
    st.markdown("<br><h3 style='color:white; text-align:center; background:#1a73e8; padding:10px; border-radius:10px;'>🛠️ لوحة القناص اليدوية (مضارب + مستثمر)</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key="x1")
    with c2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="x2")
    with c3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f", key="x3")
    
    c4, c5, c6 = st.columns(3)
    with c4: m_cl = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="x4")
    with c5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="x5")
    with c6: m_v = st.number_input("💧 سيولة اليوم:", format="%.2f", key="x6")

    if m_p > 0 and m_h > 0:
        piv = (m_h + m_l + m_p) / 3
        r1 = (2 * piv) - m_l
        s1 = (2 * piv) - m_h
        st.success(f"✅ تم الحساب يدوياً: الهدف اللحظي {r1:.3f} | الدعم {s1:.3f}")
        report_msg = f"🛠️ تحليل يدوي {u_input}\n💰 السعر: {m_p:.3f}\n🎯 هدف: {r1:.3f}\n📍 ارتكاز: {piv:.3f}"

    if report_msg:
        wa_url = f"https://wa.me/?text={report_msg.replace(' ', '%20')}"
        st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-btn-active">🚀 إرسال التقرير للواتساب الآن</a>', unsafe_allow_html=True)

st.caption("EGX Sniper v10.0 | Developed by Mostafa Adel")
