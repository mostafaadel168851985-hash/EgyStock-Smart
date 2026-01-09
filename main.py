import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعداد الصفحة
st.set_page_config(page_title="EGX Ultimate Sniper", layout="centered")

# --- CSS التصميم الاحترافي المظلم ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    
    .whatsapp-card {
        background-color: #1e2732; 
        color: white; 
        padding: 20px; 
        border-radius: 15px; 
        direction: rtl; 
        text-align: right;
        font-family: 'Arial', sans-serif;
        border: 1px solid #30363d;
        max-width: 400px;
        margin: auto;
    }
    .card-header { font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .separator { border-top: 2px solid #ffffff; margin: 10px 0; width: 100%; opacity: 0.8; }
    .info-line { font-size: 16px; margin: 8px 0; display: flex; justify-content: flex-start; align-items: center; gap: 8px; }
    .price-val { font-weight: bold; font-family: monospace; font-size: 18px; }
    
    label { color: #58a6ff !important; font-weight: bold !important; }
    .stNumberInput div div input { background-color: #0d1117 !important; color: white !important; border: 1px solid #30363d !important; }
    
    .wa-button {
        background: #25d366; color: black !important; padding: 15px; border-radius: 10px;
        text-align: center; font-weight: bold; text-decoration: none; display: block; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_analysis(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        df = stock.history(period="100d")
        if df.empty: return None
        
        p = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        vol_m = (df['Volume'].iloc[-1] * p) / 1_000_000
        
        return {
            "p": p, "chg": ((p-prev)/prev)*100, "rsi": rsi, 
            "vol": vol_m, "above_ma50": p > ma50
        }
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار البورصة الذكي</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثال: TMGH):").upper()

if u_input:
    d = get_analysis(u_input)
    
    if d:
        # حساب المستويات
        p = d['p']
        target1, target2 = p*1.02, p*1.04
        supp1, supp2 = p*0.98, p*0.96
        stop = p*0.95
        
        # عرض الكارت (بدون كود برمجي ظاهر)
        st.markdown(f"""
        <div class="whatsapp-card">
            <div class="card-header">💎 التحليل الشامل لـ {u_input}</div>
            <div class="separator"></div>
            <div class="info-line">💰 السعر المعتمد: <span class="price-val">{p:.3f}</span></div>
            <div class="info-line">📟 مؤشر RSI: <span class="price-val">{d['rsi']:.1f}</span></div>
            <div class="info-line">💧 نبض السيولة: 🔥 نشطة جداً ({d['vol']:.1f}M)</div>
            <div class="info-line">📢 التوصية: ⚖️ احتفاظ / مراقبة</div>
            <div class="separator"></div>
            <div class="info-line">🔍 الأسباب الفنية:</div>
            <div class="info-line">✅ السعر {'فوق' if d['above_ma50'] else 'تحت'} متوسط 50</div>
            <div class="info-line">✅ القوة النسبية (RSI) ممتازة</div>
            <div class="separator"></div>
            <div class="info-line">🚀 مستويات المقاومة:</div>
            <div class="info-line">🔹 هدف 1: <span class="price-val">{target1:.3f}</span></div>
            <div class="info-line">🔹 هدف 2: <span class="price-val">{target2:.3f}</span></div>
            <div class="separator"></div>
            <div class="info-line">🛡️ مستويات الدعم:</div>
            <div class="info-line">🔸 دعم 1: <span class="price-val">{supp1:.3f}</span></div>
            <div class="info-line">🔸 دعم 2: <span class="price-val">{supp2:.3f}</span></div>
            <div class="separator"></div>
            <div class="info-line">🛑 وقف الخسارة: <span class="price-val">{stop:.3f}</span></div>
        </div>
        """, unsafe_allow_html=True)

    # --- لوحة التحليل اليدوي المزدوج (6 خانات) ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة الإدخال اليدوي</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: m_p = st.number_input("💵 السعر الآن:", format="%.3f")
    with col2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f")
    with col3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f")
    
    col4, col5, col6 = st.columns(3)
    with col4: m_prev = st.number_input("↩️ إغلاق أمس:", format="%.3f")
    with col5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f")
    with col6: m_v = st.number_input("💧 سيولة (M):", format="%.2f")

    if m_p > 0:
        # زر الواتساب
        msg = f"💎 تحليل {u_input}\n💰 السعر: {m_p if m_p > 0 else d['p']}\n🚀 أهداف: {m_p*1.02:.2f}\n🛡️ دعم: {m_p*0.98:.2f}"
        wa_url = f"https://wa.me/?text={msg.replace(' ', '%20')}"
        st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-button">🚀 مشاركة التقرير على واتساب</a>', unsafe_allow_html=True)
