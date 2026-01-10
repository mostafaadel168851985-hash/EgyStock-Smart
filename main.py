import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper v16", layout="centered")

# --- CSS التنسيق الاحترافي (نفس التصميم اللي بتحبه) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .whatsapp-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        max-width: 450px; margin: 15px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .separator { border-top: 1px solid #555; margin: 12px 0; }
    .price-val { font-weight: bold; font-family: monospace; font-size: 20px; color: #4cd964; }
    .section-header { color: #3498db; font-weight: bold; margin-top: 10px; font-size: 18px; }
    .wa-link {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 15px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin: 15px auto; max-width: 280px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.03);} 100% {transform: scale(1);} }
    label { color: #58a6ff !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

def get_data(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        df = yf.Ticker(symbol).history(period="150d")
        if df.empty: return None
        p = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        vol = (df['Volume'].iloc[-1] * p) / 1_000_000
        return {"p": p, "prev": prev, "rsi": rsi, "ma50": ma50, "vol": vol}
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثل TMGH):").upper()

# --- أولاً: عرض الكارت الآلي فوراً ---
if u_input:
    d = get_data(u_input)
    if d:
        p = d['p']
        target1, target2 = p*1.025, p*1.05
        supp1 = p*0.975
        st.markdown(f"""
        <div class="whatsapp-card">
            <div style="font-size:22px; text-align:center; font-weight:bold;">💎 تقرير {u_input} (تحديث آلي)</div>
            <div class="separator"></div>
            <div style="font-size:17px;">💰 السعر اللحظي: <span class="price-val">{p:.3f}</span></div>
            <div style="font-size:17px;">📟 مؤشر RSI: <b>{d['rsi']:.1f}</b></div>
            <div style="font-size:17px;">💧 سيولة الجلسة: <b>{d['vol']:.1f}M</b></div>
            <div class="separator"></div>
            <div class="section-header">🚀 مستويات الأهداف:</div>
            <div style="font-size:17px;">🔹 هدف 1: <b>{target1:.3f}</b> | هدف 2: <b>{target2:.3f}</b></div>
            <div class="section-header">🛡️ الحماية والدعم:</div>
            <div style="font-size:17px;">🔸 دعم رئيسي: <b>{supp1:.3f}</b></div>
            <div style="font-size:17px;">🛑 وقف خسارة: <span style="color:#ff3b30;">{p*0.94:.3f}</span></div>
        </div>
        """, unsafe_allow_html=True)
        # زر واتساب للآلي
        msg_auto = f"💎 تحليل {u_input}%0A💰 السعر: {p:.3f}%0A🚀 أهداف: {target1:.3f}%0A🛡️ دعم: {supp1:.3f}"
        st.markdown(f'<a href="https://wa.me/?text={msg_auto}" target="_blank" class="wa-link">🚀 مشاركة التقرير الآلي</a>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ لم يتم العثور على بيانات آلية لهذا الرمز، يرجى استخدام اللوحة اليدوية.")

# --- ثانياً: لوحة التحليل اليدوي (مضارب + مستثمر) ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة القناص اليدوية</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key="man_p")
with col2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="man_h")
with col3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f", key="man_l")

col4, col5, col6 = st.columns(3)
with col4: m_cl = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="man_cl")
with col5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="man_mh")
with col6: m_v = st.number_input("💧 سيولة (M):", format="%.2f", key="man_v")

# كارت التحليل اليدوي (يظهر بمجرد توفر السعر وأعلى/أقل سعر)
if m_p > 0 and m_h > 0 and m_l > 0:
    piv = (m_h + m_l + m_p) / 3
    r1, r2 = (2 * piv) - m_l, piv + (m_h - m_l)
    s1 = (2 * piv) - m_h
    # هدف المستثمر بناءً على القمة الشهرية أو السعر الحالي
    inv_t = m_mh * 1.15 if m_mh > 0 else m_p * 1.20
    
    st.markdown(f"""
    <div class="whatsapp-card" style="border-right: 8px solid #3498db;">
        <div style="font-size:22px; text-align:center; font-weight:bold; color:#3498db;">🛠️ تقرير {u_input if u_input else 'يدوي'} الشامل</div>
        <div class="separator"></div>
        <div style="font-size:17px;">💰 السعر المُدخل: <span class="price-val">{m_p:.3f}</span></div>
        
        <div class="section-header">🏹 للمضارب اللحظي:</div>
        <div style="font-size:17px;">📍 نقطة الارتكاز: <b>{piv:.3f}</b></div>
        <div style="font-size:17px;">🚀 أهداف لحظية: <b>{r1:.3f} | {r2:.3f}</b></div>
        <div style="font-size:17px;">🛡️ الدعم اليومي: <b>{s1:.3f}</b></div>
        
        <div class="section-header">🏢 للمستثمر المتوسط:</div>
        <div style="font-size:17px;">🎯 الهدف القادم: <span style="color:#3498db; font-weight:bold;">{inv_t:.3f}</span></div>
        <div style="font-size:17px;">🗓️ القمة الشهرية: <b>{m_mh if m_mh > 0 else '---'}</b></div>
        <div style="font-size:17px;">💧 سيولة مرصودة: <b>{m_v:.1f}M</b></div>
        
        <div class="separator"></div>
        <div style="text-align:center; color:#ff3b30; font-weight:bold;">🛑 وقف خسارة نهائي: {s1*0.98:.3f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    msg_man = f"🎯 تحليل يدوي {u_input}%0A💰 السعر: {m_p:.3f}%0A🏹 للمضارب: {r1:.3f}%0A🏢 للمستثمر: {inv_t:.3f}%0A🛡️ دعم: {s1:.3f}"
    st.markdown(f'<a href="https://wa.me/?text={msg_man}" target="_blank" class="wa-link">🚀 مشاركة التقرير اليدوي</a>', unsafe_allow_html=True)

st.caption("EGX Ultimate Sniper v16.0 | Designed by Mostafa Adel")
