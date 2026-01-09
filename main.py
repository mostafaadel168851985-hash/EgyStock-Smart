import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعداد الصفحة
st.set_page_config(page_title="EGX Sniper Elite v8", page_icon="⚡", layout="centered")

# --- CSS التنسيق العصري ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .report-card { 
        background: white; padding: 25px; border-radius: 20px; 
        color: black; direction: rtl; text-align: right; 
        margin-bottom: 20px; border-right: 10px solid #1a73e8;
        box-shadow: 0 10px 20px rgba(255,255,255,0.1);
    }
    .price-tag { font-size: 55px; color: #d32f2f; font-weight: 900; font-family: monospace; line-height: 1; }
    label { color: #00d4ff !important; font-size: 16px !important; font-weight: bold !important; }
    .wa-btn {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; padding: 18px; border-radius: 50px;
        text-align: center; font-weight: 900; font-size: 20px;
        display: block; text-decoration: none; margin: 20px 0;
        animation: pulse-green 2s infinite;
    }
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(37, 211, 102, 0); }
        100% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }
    }
    .manual-panel { background: #111; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

def get_detailed_analysis(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        df = stock.history(period="200d")
        if df.empty: return None
        p = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        ma20, ma50, ma100 = df['Close'].rolling(20).mean().iloc[-1], df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(100).mean().iloc[-1]
        return {
            "p": p, "prev": prev, "rsi": rsi, "vol": (df['Volume'].iloc[-1]*p)/1_000_000,
            "ts": "صاعد 🟢" if p > ma20 else "هابط 🔴", "tm": "صاعد 🟢" if p > ma50 else "هابط 🔴", "tl": "صاعد 🟢" if p > ma100 else "هابط 🔴"
        }
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>⚡ EGX Sniper Elite v8</h1>", unsafe_allow_html=True)
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
            <hr>
            <b>🧭 الاتجاهات:</b> قصير: {data['ts']} | متوسط: {data['tm']} | طويل: {data['tl']}
            <hr>
            <b>🚀 المقاومات:</b> م1: {p*1.025:.3f} | م2: {p*1.050:.3f}<br>
            <b>🛡️ الدعوم:</b> د1: {p*0.975:.3f} | د2: {p*0.950:.3f}<br>
            <b>🛑 وقف الخسارة:</b> {p*0.940:.3f}
        </div>
        """, unsafe_allow_html=True)
        msg = f"⚡ تحليل {u_input}:\n💰 السعر: {p:.3f}\n🚀 أهداف: {p*1.025:.3f} - {p*1.050:.3f}\n🛡️ دعوم: {p*0.975:.3f}\n🛑 وقف: {p*0.940:.3f}"

    # --- لوحة التحليل اليدوي (المزدوجة) ---
    st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة القناص اليدوية (مضارب + مستثمر)</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="manual-panel">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key="n1")
        with c2: m_h = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="n2")
        with c3: m_l = st.number_input("📉 أقل اليوم:", format="%.3f", key="n3")
        
        c4, c5, c6 = st.columns(3)
        with c4: m_prev = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="n4")
        with c5: m_mh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="n5")
        with c6: m_v = st.number_input("💧 سيولة اليوم (M):", format="%.2f", key="n6")
        st.markdown('</div>', unsafe_allow_html=True)

        if m_p > 0 and m_h > 0:
            pivot = (m_h + m_l + m_p) / 3
            r1, r2 = (2 * pivot) - m_l, pivot + (m_h - m_l)
            s1, s2 = (2 * pivot) - m_h, pivot - (m_h - m_l)
            
            st.markdown(f"""
            <div class="report-card" style="border-top-color: #00c853;">
                <h2 style="margin:0;">✅ نتيجة التحليل اليدوي</h2>
                <div class="price-tag">{m_p:.3f}</div>
                <hr>
                <b>🏹 أهداف المضارب:</b> م1: {r1:.3f} | م2: {r2:.3f}<br>
                <b>🛡️ دعوم المضارب:</b> د1: {s1:.3f} | د2: {s2_d if 's2_d' in locals() else s2:.3f}<br>
                <b>🏢 هدف المستثمر:</b> {m_mh*1.1:.3f}<br>
                <b>📍 الارتكاز:</b> {pivot:.3f}
            </div>
            """, unsafe_allow_html=True)
            msg = f"🛠️ يدوي {u_input}:\n💰 السعر: {m_p:.3f}\n🚀 أهداف: {r1:.3f} - {r2:.3f}\n🛡️ دعوم: {s1:.3f}\n📍 الارتكاز: {pivot:.3f}"

    if msg:
        wa_url = f"https://wa.me/?text={msg.replace(' ', '%20').replace('', '%0A')}"
        st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-btn">🚀 إرسال التقرير للواتساب الآن</a>', unsafe_allow_html=True)

st.caption("EGX Sniper Elite v8.0 | مصطفى عادل 2026")
