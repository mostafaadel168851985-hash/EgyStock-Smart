import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Sniper v30", layout="centered")

# --- CSS التنسيق الاحترافي الموحد ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        margin: 10px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .separator { border-top: 1px solid #444; margin: 12px 0; }
    .price-large { font-weight: bold; font-size: 36px; color: #4cd964; text-align: center; display: block; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 17px; margin-bottom: 5px; }
    .info-line { margin: 8px 0; font-size: 15px; display: flex; justify-content: space-between; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 12px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

ARABIC_NAMES = {
    "ATQA": "مصر الوطنية للصلب - عتاقة", "SWDY": "السويدي إليكتريك",
    "TMGH": "مجموعة طلعت مصطفى", "MOED": "المصرية لنظم التعليم الحديث",
    "FWRY": "فوري لتكنولوجيا المدفوعات", "COMI": "البنك التجاري الدولي",
    "CRST": "كريستمارك للمقاولات"
}

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز للبحث السريع (مثلاً ATQA):").upper()

# --- 1. التحليل الآلي اللحظي ---
if u_input:
    try:
        symbol = f"{u_input}.CA"
        df = yf.Ticker(symbol).history(period="150d")
        if not df.empty:
            p = df['Close'].iloc[-1]
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            vol_val = (df['Volume'].iloc[-1] * p) / 1_000_000
            ma50 = df['Close'].rolling(50).mean().iloc[-1]
            name_ar = ARABIC_NAMES.get(u_input, "شركة متداولة")
            
            liq_status = "طبيعية ⚖️" if vol_val > 10 else "ضعيفة ⚠️"
            recommendation = "احتفاظ / مراقبة ⚖️" if rsi < 70 else "جني أرباح جزئي ⚠️"
            if rsi < 35: recommendation = "تجميع / شراء 🟢"

            st.markdown(f"""
            <div class="report-card">
                <div style="text-align:center;"><span style="color:#3498db;">💎 التحليل الآلي لـ {u_input}</span><br><b>{name_ar}</b></div>
                <div class="separator"></div>
                <div class="info-line"><span>💰 السعر المعتمد:</span> <b>{p:.3f}</b></div>
                <div class="info-line"><span>📟 مؤشر RSI:</span> <b>{rsi:.1f}</b></div>
                <div class="info-line"><span>💧 نبض السيولة:</span> <b>{liq_status}</b></div>
                <div class="info-line"><span>📢 التوصية:</span> <b>{recommendation}</b></div>
                <div class="separator"></div>
                <div class="label-blue">🔍 الأسباب الفنية:</div>
                <div class="info-line"><span>✅ السعر فوق متوسط 50:</span> <b>{'نعم' if p > ma50 else 'لا'}</b></div>
                <div class="info-line"><span>✅ القوة النسبية (RSI):</span> <b>{'متوازنة' if rsi < 65 else 'تشبع شرائي'}</b></div>
                <div class="separator"></div>
                <div class="label-blue">🚀 مستويات المقاومة:</div>
                <div class="info-line"><span>🔹 هدف 1: <b>{p*1.025:.3f}</b></span> <span>🔹 هدف 2: <b>{p*1.05:.3f}</b></span></div>
                <div class="label-blue">🛡️ مستويات الدعم:</div>
                <div class="info-line"><span>🔸 دعم 1: <b>{p*0.975:.3f}</b></span> <span>🔸 دعم 2: <b>{p*0.95:.3f}</b></span></div>
                <div class="separator"></div>
                <div class="label-blue">🏹 قسم المضارب والمستثمر:</div>
                <div class="info-line"><span>🚀 هدف مضاربي: <b>{p*1.03:.3f}</b></span> <span>🎯 هدف مستثمر: <b>{p*1.20:.3f}</b></span></div>
                <div class="separator"></div>
                <div style="color:#ff3b30; text-align:center; font-weight:bold;">🛑 وقف الخسارة: {p*0.94:.3f}</div>
            </div>
            """, unsafe_allow_html=True)
    except: pass

st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة القناص اليدوية (المطورة)</h3>", unsafe_allow_html=True)

# --- 2. التحليل اليدوي (بناءً على طلبك الجديد) ---
col1, col2, col3 = st.columns(3)
with col1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key="man_p")
with col2: m_h = st.number_input("🔝 أعلى سعر اليوم:", format="%.3f", key="man_h")
with col3: m_l = st.number_input("📉 أقل سعر اليوم:", format="%.3f", key="man_l")

col4, col5, col6 = st.columns(3)
with col4: m_close = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="man_c")
with col5: m_mhigh = st.number_input("🗓️ أعلى سعر شهر:", format="%.3f", key="man_mh")
with col6: m_vol = st.number_input("💧 السيولة (M):", format="%.2f", key="man_v")

col7, col8 = st.columns(2)
with col7: m_rsi_status = st.selectbox("📟 وضع مؤشر RSI:", ["هادئ (تحت 40)", "متوسط (40-60)", "مرتفع (فوق 70)"])
with col8: m_ma_status = st.selectbox("📈 هل السعر فوق متوسط 50؟", ["نعم", "لا"])

if m_p > 0 and m_h > 0:
    name_man = ARABIC_NAMES.get(u_input if u_input else "", "سهم يدوي")
    # منطق التوصية اليدوية
    rec_m = "مراقبة ⚖️"
    if m_rsi_status == "هادئ (تحت 40)": rec_m = "شراء / تجميع 🟢"
    elif m_rsi_status == "مرتفع (فوق 70)": rec_m = "جني أرباح جزئي ⚠️"

    st.markdown(f"""
    <div class="report-card" style="border-right: 8px solid #3498db;">
        <div style="text-align:center;"><span style="color:#3498db;">🛠️ التقرير اليدوي الشامل</span><br><b>{name_man}</b></div>
        <div class="separator"></div>
        <div class="info-line"><span>💰 السعر الحالي:</span> <b>{m_p:.3f}</b></div>
        <div class="info-line"><span>🔙 إغلاق أمس:</span> <b>{m_close:.3f}</b></div>
        <div class="info-line"><span>💧 نبض السيولة:</span> <b>{'طبيعية ⚖️' if m_vol > 10 else 'ضعيفة ⚠️'}</b></div>
        <div class="info-line"><span>📢 التوصية:</span> <b>{rec_m}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🔍 الأسباب الفنية:</div>
        <div class="info-line"><span>✅ فوق متوسط 50:</span> <b>{m_ma_status}</b></div>
        <div class="info-line"><span>✅ حالة RSI:</span> <b>{m_rsi_status}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🚀 مستويات المقاومة:</div>
        <div class="info-line"><span>🔹 هدف 1: <b>{m_p*1.025:.3f}</b></span> <span>🔹 هدف 2: <b>{m_p*1.05:.3f}</b></span></div>
        <div class="label-blue">🛡️ مستويات الدعم:</div>
        <div class="info-line"><span>🔸 دعم 1: <b>{m_p*0.975:.3f}</b></span> <span>🔸 دعم 2: <b>{m_p*0.95:.3f}</b></span></div>
        <div class="separator"></div>
        <div class="label-blue">🏹 قسم المضارب والمستثمر:</div>
        <div class="info-line"><span>🚀 هدف مضاربي: <b>{m_p*1.03:.3f}</b></span> <span>🎯 هدف مستثمر: <b>{m_p*1.20:.3f}</b></span></div>
        <div class="info-line"><span>🗓️ قمة شهرية: <b>{m_mhigh:.3f}</b></span></div>
        <div class="separator"></div>
        <div style="color:#ff3b30; text-align:center; font-weight:bold;">🛑 وقف الخسارة: {m_p*0.94:.3f}</div>
    </div>
    """, unsafe_allow_html=True)
