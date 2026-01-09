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
    }
    .section-title { 
        color: #1a73e8; font-weight: bold; border-bottom: 2px solid #eee; 
        margin: 15px 0 10px 0; padding-bottom: 5px; font-size: 18px;
    }
    .price-val { font-size: 55px; color: #d32f2f; font-weight: 900; font-family: monospace; line-height: 1; }
    .manual-panel {
        background: #111; padding: 20px; border-radius: 12px; 
        border: 2px solid #00c853; color: white; margin-top: 20px;
    }
    .whatsapp-box {
        border: 2px solid #25d366; padding: 15px; border-radius: 10px;
        background: #0a0a0a; color: #25d366; margin-top: 10px;
    }
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
u_input = st.text_input("🔍 ادخل رمز السهم (مثل ATQA, MOED, CRST):", "").strip().upper()

if u_input:
    auto = get_auto_analysis(u_input)
    report_text = "" 
    
    if auto:
        p = auto['p']
        change = ((p - auto['prev']) / auto['prev']) * 100
        # حسابات دعم ومقاومة آلية تقريبية (بناءً على النسبة المئوية)
        st.markdown(f"""
        <div class="report-card">
            <h3 style="margin:0;">💎 التقرير الشامل لـ {u_input} (آلي)</h3>
            <div class="price-val">{p:.3f}</div>
            <b style="color:{'green' if change > 0 else 'red'}; font-size:20px;">{change:+.2f}%</b>
            <p>RSI: {auto['rsi']:.1f} | سيولة الجلسة: {auto['vol']:.2f}M</p>
            
            <div class="section-title">🔍 بوصلة الاتجاهات</div>
            • قصير: {auto['ts']} | متوسط: {auto['tm']} | طويل: {auto['tl']}
            
            <div class="section-title">🚀 مستويات المقاومة (الأهداف)</div>
            • مقاومة 1: {p*1.025:.3f} 🔷 | مقاومة 2: {p*1.05:.3f} 🔷
            
            <div class="section-title">🛡️ مستويات الدعم</div>
            • دعم 1: {p*0.975:.3f} 🔸 | دعم 2: {p*0.95:.3f} 🔸
            
            <div class="section-title">🛑 وقف الخسارة النهائى</div>
            • {p*0.94:.3f} 🛑
        </div>
        """, unsafe_allow_html=True)
        
        report_text = f"📊 تحليل {u_input}:\n💰 السعر: {p:.3f}\n🚀 أهداف: {p*1.025:.3f} - {p*1.05:.3f}\n🛡️ دعوم: {p*0.975:.3f}\n🛑 وقف: {p*0.94:.3f}"

    # 2. لوحة التحليل المزدوج
    st.markdown("###") 
    with st.expander("🛠️ لوحة التحليل المزدوج (يدوي / مضارب ومستثمر)", expanded=not auto):
        st.markdown("<div class='manual-panel'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: m_price = st.number_input("السعر الآن:", format="%.3f", step=0.001, key="m1")
        with col2: m_high = st.number_input("أعلى سعر اليوم:", format="%.3f", step=0.001, key="m2")
        with col3: m_low = st.number_input("أقل سعر اليوم:", format="%.3f", step=0.001, key="m3")
        
        st.write("📈 **بيانات المستثمر والسيولة:**")
        col4, col5, col6 = st.columns(3)
        with col4: mh = st.number_input("أعلى سعر شهر:", format="%.3f", key="m4")
        with col5: v_today = st.number_input("سيولة اليوم:", format="%.2f", key="m5")
        with col6: v_avg = st.number_input("متوسط السيولة:", format="%.2f", key="m6")
        st.markdown("</div>", unsafe_allow_html=True)

        if m_price > 0 and m_high > 0:
            piv = (m_high + m_low + m_price) / 3
            r1_d = (2 * piv) - m_low
            r2_d = piv + (m_high - m_low)
            s1_d = (2 * piv) - m_high
            s2_d = piv - (m_high - m_low)
            
            st.markdown(f"""
            <div class="report-card" style="border-top-color: #00c853;">
                <h3>📊 نتيجة التحليل اليدوي لـ {u_input}</h3>
                <div class="price-val">{m_price:.3f}</div>
                <hr>
                <div class="section-title">🏹 أهداف المضارب (المقاومات)</div>
                • مقاومة 1: {r1_d:.3f} 🔷 | مقاومة 2: {r2_d:.3f} 🔷
                <div class="section-title">🛡️ دعوم المضارب</div>
                • دعم 1: {s1_d:.3f} 🔸 | دعم 2: {s2_d:.3f} 🔸
                <div class="section-title">📍 نقطة الارتكاز (Pivot)</div>
                • {piv:.3f}
            </div>
            """, unsafe_allow_html=True)
            
            report_text = f"🛠️ تحليل يدوي {u_input}:\n💰 السعر: {m_price:.3f}\n🚀 أهداف: {r1_d:.3f} - {r2_d:.3f}\n🛡️ دعوم: {s1_d:.3f}\n📍 ارتكاز: {piv:.3f}"

    # زر النسخ للواتساب في صندوق أخضر واضح
    if report_text:
        st.markdown(f"""
        <div class="whatsapp-box">
            <b>📱 نص التقرير الجاهز للنسخ:</b><br><br>
            {report_text.replace('\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)
        st.button("نسخ النص (اضغط مطولاً للنسخ بالهاتف)", on_click=None)

st.caption("تطوير: مصطفى عادل | EGX Smart Sniper 2026")
