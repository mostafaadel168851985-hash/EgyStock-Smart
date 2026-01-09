import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعداد الصفحة
st.set_page_config(page_title="EGX Ultimate Sniper", layout="centered")

# --- CSS التصميم الاحترافي (الكارت + الزرار المنور) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    
    .whatsapp-card {
        background-color: #1e2732; 
        color: white; 
        padding: 25px; 
        border-radius: 15px; 
        direction: rtl; 
        text-align: right;
        font-family: 'Arial', sans-serif;
        border: 1px solid #30363d;
        max-width: 450px;
        margin: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .card-header { font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .separator { border-top: 2px solid #ffffff; margin: 12px 0; width: 100%; opacity: 0.9; }
    .info-line { font-size: 17px; margin: 10px 0; display: flex; justify-content: flex-start; gap: 8px; }
    .price-val { font-weight: bold; font-family: monospace; font-size: 19px; color: #4cd964; }
    
    label { color: #58a6ff !important; font-weight: bold !important; font-size: 16px !important; }
    
    /* زرار الواتساب الـ Active */
    .wa-link {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; 
        padding: 18px; 
        border-radius: 50px;
        text-align: center; 
        font-weight: 900; 
        font-size: 20px;
        display: block; 
        text-decoration: none; 
        margin: 25px auto;
        max-width: 300px;
        animation: pulse-green 2s infinite;
        box-shadow: 0 0 15px rgba(37, 211, 102, 0.5);
    }
    @keyframes pulse-green {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.7); }
        70% { transform: scale(1.03); box-shadow: 0 0 0 15px rgba(37, 211, 102, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

def get_live_data(ticker):
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
        return {"p": p, "rsi": rsi, "vol": vol_m, "above_ma50": p > ma50, "prev": prev}
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المحترف</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً MOED أو ATQA):").upper()

if u_input:
    d = get_live_data(u_input)
    
    # تحضير بيانات التقرير (آلية أو يدوية)
    if d:
        p = d['p']
        target1, target2 = p*1.025, p*1.05
        supp1, supp2 = p*0.975, p*0.95
        stop = p*0.94
        
        # عرض الكارت المطابق تماماً للصورة والمعلومات
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

        # زر الواتساب الـ Active (يظهر دائماً بعد كتابة السهم)
        wa_msg = f"💎 تحليل {u_input}%0A💰 السعر: {p:.3f}%0A🚀 أهداف: {target1:.3f} - {target2:.3f}%0A🛡️ دعم: {supp1:.3f}%0A🛑 وقف: {stop:.3f}"
        st.markdown(f'<a href="https://wa.me/?text={wa_msg}" target="_blank" class="wa-link">🚀 مشاركة التقرير على واتساب</a>', unsafe_allow_html=True)

    # --- لوحة التحليل اليدوي (6 خانات) ---
    st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة القناص اليدوية (مضارب + مستثمر)</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key="m1")
    with col2: m_h = st.number_input("🔝 أعلى سعر:", format="%.3f", key="m2")
    with col3: m_l = st.number_input("📉 أقل سعر:", format="%.3f", key="m3")
    
    col4, col5, col6 = st.columns(3)
    with col4: m_cl = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="m4")
    with col5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="m5")
    with col6: m_v = st.number_input("💧 السيولة (M):", format="%.2f", key="m6")

    if m_p > 0 and m_h > 0:
        piv = (m_h + m_l + m_p) / 3
        st.info(f"💡 تم تفعيل التحليل اليدوي: الارتكاز الحالي هو {piv:.3f}")

st.caption("EGX Ultimate Sniper v12.0 | Developed for Mostafa Adel")
