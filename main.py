import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper v22", layout="centered")

# --- CSS التنسيق الاحترافي الكامل ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        max-width: 500px; margin: 15px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .separator { border-top: 1px solid #444; margin: 12px 0; }
    .price-large { font-weight: bold; font-size: 32px; color: #4cd964; text-align: center; display: block; margin: 10px 0; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 18px; margin-top: 10px; }
    .info-line { margin: 8px 0; font-size: 16px; display: flex; justify-content: space-between; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 12px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 20px; font-size: 18px;
    }
    .trend-tag { padding: 2px 8px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def get_full_analysis(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        df = yf.Ticker(symbol).history(period="150d")
        if df.empty: return None
        p = df['Close'].iloc[-1]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        vol = (df['Volume'].iloc[-1] * p) / 1_000_000
        # حساب الاتجاهات
        ma20, ma50, ma100 = df['Close'].rolling(20).mean().iloc[-1], df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(100).mean().iloc[-1]
        return {
            "p": p, "rsi": rsi, "vol": vol,
            "t_s": "صاعد 🟢" if p > ma20 else "هابط 🔴",
            "t_m": "صاعد 🟢" if p > ma50 else "هابط 🔴",
            "t_l": "صاعد 🟢" if p > ma100 else "هابط 🔴"
        }
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً ATQA أو CRST):").upper()

# --- 1. التقرير الآلي (الكامل) ---
if u_input:
    d = get_full_analysis(u_input)
    if d:
        r1, r2 = d['p']*1.025, d['p']*1.05
        s1, s2 = d['p']*0.975, d['p']*0.95
        st_loss = d['p']*0.94
        
        st.markdown(f"""
        <div class="report-card">
            <div style="text-align:center; font-size:22px; font-weight:bold;">💎 تحليل {u_input} (تحديث آلي)</div>
            <div class="separator"></div>
            <span class="price-large">{d['p']:.3f}</span>
            <div class="info-line"><span>📟 مؤشر RSI: <b>{d['rsi']:.1f}</b></span> <span>💧 سيولة الجلسة: <b>{d['vol']:.1f}M</b></span></div>
            <div class="separator"></div>
            <div class="label-blue">🔍 اتجاهات السهم (Trend):</div>
            <div class="info-line"><span>مدى قصير: {d['t_s']}</span> <span>مدى متوسط: {d['t_m']}</span></div>
            <div class="info-line"><span>مدى طويل: {d['t_l']}</span></div>
            <div class="separator"></div>
            <div class="label-blue">🚀 مستويات المقاومة (الأهداف):</div>
            <div class="info-line"><span>🎯 هدف 1: <b>{r1:.3f}</b></span> <span>🎯 هدف 2: <b>{r2:.3f}</b></span></div>
            <div class="separator"></div>
            <div class="label-blue">🛡️ مستويات الدعم والحماية:</div>
            <div class="info-line"><span>🔸 دعم 1: <b>{s1:.3f}</b></span> <span>🔸 دعم 2: <b>{s2:.3f}</b></span></div>
            <div class="info-line" style="color:#ff3b30; font-weight:bold; justify-content:center;">🛑 وقف الخسارة: {st_loss:.3f}</div>
        """, unsafe_allow_html=True)
        
        msg = f"🎯 تحليل {u_input}%0A💰 السعر: {d['p']:.3f}%0A🚀 أهداف: {r1:.3f} - {r2:.3f}%0A🛡️ دعم: {s1:.3f}%0A🛑 وقف: {st_loss:.3f}"
        st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank" class="wa-button">🚀 مشاركة التقرير الآلي</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 2. لوحة الإدخال اليدوي (الشاملة + تصفير ذكي) ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة الإدخال اليدوي الشاملة</h3>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key=f"p_{u_input}")
with c2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f", key=f"h_{u_input}")
with c3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f", key=f"l_{u_input}")

c4, c5, c6 = st.columns(3)
with c4: m_cl = st.number_input("↩️ إغلاق أمس:", format="%.3f", key=f"c_{u_input}")
with c5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key=f"mh_{u_input}")
with c6: m_v = st.number_input("💧 (M) سيولة:", format="%.2f", key=f"v_{u_input}")

if m_p > 0 and m_h > 0:
    piv = (m_h + m_l + m_p) / 3
    mr1, mr2 = (2 * piv) - m_l, piv + (m_h - m_l)
    ms1, ms2 = (2 * piv) - m_h, piv - (m_h - m_l)
    m_trend = "صاعد 🟢" if m_p > m_cl else "هابط 🔴"
    
    st.markdown(f"""
    <div class="report-card" style="border-right: 8px solid #3498db;">
        <div style="text-align:center; font-size:22px; font-weight:bold; color:#3498db;">🛠️ تقرير {u_input if u_input else 'يدوي'} الشامل</div>
        <div class="separator"></div>
        <span class="price-large">{m_p:.3f}</span>
        <div class="info-line"><span>📍 نقطة الارتكاز: <b>{piv:.3f}</b></span> <span>💧 السيولة: <b>{m_v:.1f}M</b></span></div>
        <div class="separator"></div>
        <div class="label-blue">🏹 قسم المضارب:</div>
        <div class="info-line"><span>📈 الاتجاه اللحظي: {m_trend}</span></div>
        <div class="info-line"><span>🚀 هدف 1: <b>{mr1:.3f}</b></span> <span>🚀 هدف 2: <b>{mr2:.3f}</b></span></div>
        <div class="info-line"><span>🛡️ دعم 1: <b>{ms1:.3f}</b></span> <span>🛡️ دعم 2: <b>{ms2:.3f}</b></span></div>
        <div class="separator"></div>
        <div class="label-blue">🏢 قسم المستثمر:</div>
        <div class="info-line"><span>🗓️ القمة الشهرية: <b>{m_mh:.3f}</b></span> <span>🎯 الهدف المتوقع: <b>{m_p*1.20:.3f}</b></span></div>
        <div class="separator"></div>
        <div class="info-line" style="color:#ff3b30; font-weight:bold; justify-content:center;">🛑 وقف الخسارة اليدوي: {ms1*0.98:.3f}</div>
    """, unsafe_allow_html=True)
    
    msg_m = f"🛠️ تحليل يدوي {u_input}%0A💰 السعر: {m_p:.3f}%0A🚀 أهداف: {mr1:.3f} - {mr2:.3f}%0A🛡️ دعم: {ms1:.3f}%0A🛑 وقف: {ms1*0.98:.3f}"
    st.markdown(f'<a href="https://wa.me/?text={msg_m}" target="_blank" class="wa-button">🚀 مشاركة التقرير اليدوي</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.caption("EGX Ultimate Sniper v22.0 | Full Data & Smart Reset")
