import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper v17", layout="centered")

# --- CSS التنسيق النهائي ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .whatsapp-card {
        background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        max-width: 450px; margin: 10px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .separator { border-top: 1px solid #444; margin: 10px 0; }
    .price-val { font-weight: bold; font-family: monospace; font-size: 20px; color: #4cd964; }
    .label-blue { color: #3498db; font-weight: bold; }
    .wa-link {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 15px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin: 10px auto; max-width: 280px;
    }
    </style>
    """, unsafe_allow_html=True)

def analyze_trend(df):
    p = df['Close'].iloc[-1]
    ma20 = df['Close'].rolling(20).mean().iloc[-1]
    ma50 = df['Close'].rolling(50).mean().iloc[-1]
    ma100 = df['Close'].rolling(100).mean().iloc[-1]
    return {
        "short": "صاعد 🟢" if p > ma20 else "هابط 🔴",
        "mid": "صاعد 🟢" if p > ma50 else "هابط 🔴",
        "long": "صاعد 🟢" if p > ma100 else "هابط 🔴"
    }

def get_data(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        df = yf.Ticker(symbol).history(period="200d")
        if df.empty: return None
        p = df['Close'].iloc[-1]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        vol = (df['Volume'].iloc[-1] * p) / 1_000_000
        trends = analyze_trend(df)
        return {"p": p, "rsi": rsi, "vol": vol, "trends": trends}
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثل TMGH):").upper()

# --- الكارت الآلي ---
if u_input:
    d = get_data(u_input)
    if d:
        p = d['p']
        # حساب الدعوم والمقاومات
        r1, r2 = p*1.025, p*1.05
        s1, s2 = p*0.975, p*0.95
        
        st.markdown(f"""
        <div class="whatsapp-card">
            <div style="font-size:20px; text-align:center; font-weight:bold;">💎 التحليل الشامل لـ {u_input}</div>
            <div class="separator"></div>
            <div>💰 السعر المعتمد: <span class="price-val">{p:.3f}</span></div>
            <div>📟 مؤشر RSI: <b>{d['rsi']:.1f}</b></div>
            <div>💧 نبض السيولة: 🔥 ({d['vol']:.1f}M)</div>
            <div class="separator"></div>
            <div class="label-blue">🔍 الاتجاهات:</div>
            <div>• مدى قصير: {d['trends']['short']}</div>
            <div>• مدى متوسط: {d['trends']['mid']}</div>
            <div>• مدى طويل: {d['trends']['long']}</div>
            <div class="separator"></div>
            <div class="label-blue">🚀 مستويات المقاومة:</div>
            <div>🔹 هدف 1: <b>{r1:.3f}</b> | 🔹 هدف 2: <b>{r2:.3f}</b></div>
            <div class="separator"></div>
            <div class="label-blue">🛡️ مستويات الدعم:</div>
            <div>🔸 دعم 1: <b>{s1:.3f}</b> | 🔸 دعم 2: <b>{s2:.3f}</b></div>
            <div class="separator"></div>
            <div style="color:#ff3b30; font-weight:bold;">🛑 وقف الخسارة: {p*0.94:.3f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        msg = f"💎 تحليل {u_input}%0A💰 السعر: {p:.3f}%0A🚀 أهداف: {r1:.3f} - {r2:.3f}%0A🛡️ دعم: {s1:.3f}%0A🛑 وقف: {p*0.94:.3f}"
        st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank" class="wa-link">🚀 مشاركة التقرير الآلي</a>', unsafe_allow_html=True)

# --- الكارت اليدوي (مصلح تماماً) ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة الإدخال اليدوية</h3>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key="m1")
with c2: m_h = st.number_input("🔝 أعلى سعر:", format="%.3f", key="m2")
with c3: m_l = st.number_input("📉 أقل سعر:", format="%.3f", key="m3")

c4, c5, c6 = st.columns(3)
with c4: m_cl = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="m4")
with c5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="m5")
with c6: m_v = st.number_input("💧 السيولة (M):", format="%.2f", key="m6")

if m_p > 0 and m_h > 0:
    piv = (m_h + m_l + m_p) / 3
    mr1, mr2 = (2 * piv) - m_l, piv + (m_h - m_l)
    ms1, ms2 = (2 * piv) - m_h, piv - (m_h - m_l)
    
    # تحديد الاتجاه اليدوي بناءً على السعر وإغلاق أمس والارتكاز
    manual_trend = "صاعد 🟢" if m_p > m_cl and m_p > piv else "هابط 🔴"

    st.markdown(f"""
    <div class="whatsapp-card" style="border-right: 5px solid #3498db;">
        <div style="font-size:20px; text-align:center; font-weight:bold; color:#3498db;">🛠️ تقرير {u_input if u_input else ''} اليدوي الشامل</div>
        <div class="separator"></div>
        <div>💰 السعر المُدخل: <span class="price-val">{m_p:.3f}</span></div>
        <div>📍 نقطة الارتكاز: <b>{piv:.3f}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🏹 قسم المضارب:</div>
        <div>• الاتجاه اللحظي: {manual_trend}</div>
        <div>🚀 هدف 1: <b>{mr1:.3f}</b> | 🚀 هدف 2: <b>{mr2:.3f}</b></div>
        <div>🛡️ دعم 1: <b>{ms1:.3f}</b> | 🛡️ دعم 2: <b>{ms2:.3f}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🏢 قسم المستثمر:</div>
        <div>🗓️ القمة الشهرية: <b>{m_mh:.3f}</b></div>
        <div>🎯 الهدف المتوقع: <b>{m_p*1.20:.3f}</b></div>
        <div>💧 السيولة: <b>{m_v:.1f}M</b></div>
        <div class="separator"></div>
        <div style="color:#ff3b30; font-weight:bold;">🛑 وقف الخسارة: {ms1*0.98:.3f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    wa_m = f"🛠️ تحليل يدوي {u_input}%0A💰 السعر: {m_p:.3f}%0A🚀 أهداف: {mr1:.3f} - {mr2:.3f}%0A🛡️ دعم: {ms1:.3f}%0A🛑 وقف: {ms1*0.98:.3f}"
    st.markdown(f'<a href="https://wa.me/?text={wa_m}" target="_blank" class="wa-link">🚀 مشاركة التقرير اليدوي</a>', unsafe_allow_html=True)

st.caption("EGX Ultimate Sniper v17.0 | Fixed UI & Data")
