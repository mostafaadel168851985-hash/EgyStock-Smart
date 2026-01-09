import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعداد الصفحة
st.set_page_config(page_title="EGX Pro Sniper", page_icon="🎯", layout="centered")

# --- تنسيق الواجهة الاحترافي ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .report-card { 
        background: white; padding: 25px; border-radius: 15px; 
        color: black; direction: rtl; text-align: right; 
        margin-bottom: 20px; border-top: 8px solid #1a73e8;
        box-shadow: 0 4px 15px rgba(255,255,255,0.1);
    }
    .section-title { 
        color: #1a73e8; font-weight: bold; border-bottom: 2px solid #eee; 
        margin: 15px 0 10px 0; padding-bottom: 5px; font-size: 18px;
    }
    .price-val { font-size: 50px; color: #d32f2f; font-weight: 900; font-family: monospace; line-height: 1; }
    .manual-panel {
        background: #111; padding: 20px; border-radius: 12px; 
        border: 2px solid #00c853; color: white; margin-top: 20px;
    }
    .stNumberInput label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- وظيفة جلب البيانات الآلية ---
def get_auto_analysis(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        df = stock.history(period="150d")
        df_now = stock.history(period="1d", interval="1m")
        if df.empty: return None
        
        p = df_now['Close'].iloc[-1] if not df_now.empty else df['Close'].iloc[-1]
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma100 = df['Close'].rolling(100).mean().iloc[-1]
        
        return {
            "p": p, "rsi": df['RSI'].iloc[-1],
            "ts": "صاعد 🟢" if p > ma10 else "هابط 🔴",
            "tm": "صاعد 🟢" if p > ma50 else "هابط 🔴",
            "tl": "صاعد 🟢" if p > ma100 else "هابط 🔴",
            "prev": stock.info.get('previousClose', df['Close'].iloc[-2]),
            "vol": (df['Volume'].iloc[-1] * p) / 1_000_000
        }
    except: return None

# --- واجهة المستخدم ---
st.markdown("<h1 style='text-align:center; color:white;'>🎯 EGX Ultimate Sniper</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل رمز السهم (مثلاً ATQA, MOED, CRST):", "").strip().upper()

if u_input:
    auto = get_auto_analysis(u_input)
    report_text = "" # نص للنسخ
    
    if auto:
        change = ((auto['p'] - auto['prev']) / auto['prev']) * 100
        st.markdown(f"""
        <div class="report-card">
            <h3 style="margin:0;">💎 التقرير الشامل لـ {u_input} (آلي)</h3>
            <div class="price-val">{auto['p']:.3f}</div>
            <b style="color:{'green' if change > 0 else 'red'}; font-size:20px;">{change:+.2f}%</b>
            <p>RSI: {auto['rsi']:.1f} | سيولة الجلسة: {auto['vol']:.2f}M</p>
            <div class="section-title">🔍 بوصلة الاتجاهات</div>
            • قصير: {auto['ts']} | متوسط: {auto['tm']} | طويل: {auto['tl']}
            <div class="section-title">🚀 مستويات المقاومة (أهداف)</div>
            • هدف 1: {auto['p']*1.03:.3f} | هدف 2: {auto['p']*1.06:.3f}
            <div class="section-title">🛑 مستويات الحماية</div>
            • وقف خسارة: {auto['p']*0.96:.3f}
        </div>
        """, unsafe_allow_html=True)
        
        report_text = f"📊 تحليل {u_input}:\n💰 السعر: {auto['p']:.3f}\n📈 اتجاه قصير: {auto['ts']}\n🚀 أهداف: {auto['p']*1.03:.3f} - {auto['p']*1.06:.3f}\n🛑 وقف: {auto['p']*0.96:.3f}"

    # 2. لوحة التحليل اليدوي
    with st.container():
        st.markdown("<div class='manual-panel'>", unsafe_allow_html=True)
        st.markdown("### 🛠️ لوحة التحليل المزدوج (يدوي)")
        
        st.markdown("<b style='color:#00c853;'>❶ للمضارب (اليوم):</b>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: m_price = st.number_input("السعر الآن:", format="%.3f", step=0.001, key="m1")
        with c2: m_high = st.number_input("أعلى سعر:", format="%.3f", step=0.001, key="m2")
        with c3: m_low = st.number_input("أقل سعر:", format="%.3f", step=0.001, key="m3")
        
        st.markdown("<br><b style='color:#ffcc00;'>❷ للمستثمر (شهري):</b>", unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        with c4: mh = st.number_input("أعلى سعر شهر:", format="%.3f", key="m4")
        with c5: ml = st.number_input("أقل سعر شهر:", format="%.3f", key="m5")
        
        st.markdown("</div>", unsafe_allow_html=True)

        if m_price > 0 and m_high > 0:
            piv = (m_high + m_low + m_price) / 3
            r1_d = (2 * piv) - m_low
            s1_d = (2 * piv) - m_high
            
            st.markdown(f"""
            <div class="report-card" style="border-top-color: #00c853; margin-top:20px;">
                <h3>📊 نتيجة التحليل اليدوي لـ {u_input}</h3>
                <div class="price-val">{m_price:.3f}</div>
                <div class="section-title">🏹 أهداف المضارب</div>
                • نقطة الارتكاز: {piv:.3f}<br>
                • هدف لحظي: {r1_d:.3f} | وقف: {s1_d:.3f}
            </div>
            """, unsafe_allow_html=True)
            
            report_text = f"🛠️ تحليل يدوي {u_input}:\n💰 السعر: {m_price:.3f}\n📍 ارتكاز: {piv:.3f}\n🚀 هدف: {r1_d:.3f}\n🛑 وقف: {s1_d:.3f}"

    # زر النسخ للواتساب
    if report_text:
        st.write("---")
        st.text_area("انسخ هذا النص لمشاركته:", report_text, height=150)
        st.info("💡 حدد النص بالأعلى وانقر 'Copy' ثم الصقه في واتساب أو تليجرام.")

st.caption("برمجة وتطوير: مصطفى عادل | بيانات البورصة المصرية 🎯")
