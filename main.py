import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعداد الصفحة
st.set_page_config(page_title="EGX Pro Sniper", page_icon="🎯", layout="centered")

# --- تنسيق الواجهة الاحترافي (إصلاح شامل) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    
    /* تنسيق الكارت الأبيض */
    .report-card { 
        background: white; padding: 20px; border-radius: 15px; 
        color: black; direction: rtl; text-align: right; 
        margin-bottom: 20px; border-top: 8px solid #1a73e8;
    }
    
    /* تنسيق العناوين داخل الكارت */
    .section-header { 
        color: #1a73e8; font-weight: bold; border-bottom: 1px solid #ddd; 
        margin: 10px 0; padding-bottom: 5px; font-size: 16px;
    }

    /* سعر السهم الكبير */
    .price-val { font-size: 50px; color: #d32f2f; font-weight: 900; font-family: monospace; line-height: 1.1; }

    /* الزرار اليدوي المنور */
    .stExpander {
        background-color: #1a1a1a !important;
        border: 3px solid #ffffff !important;
        border-radius: 12px !important;
        margin-top: 20px !important;
    }
    .stExpander p { color: white !important; font-weight: bold !important; font-size: 18px !important; }

    /* لوحة الإدخال اليدوي */
    .manual-panel {
        background: #000; padding: 15px; border-radius: 10px; color: white;
    }
    
    /* صندوق الواتساب */
    .whatsapp-box {
        border: 2px solid #25d366; padding: 15px; border-radius: 10px;
        background: #050505; color: #25d366; margin-top: 15px; text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

# --- وظيفة جلب البيانات ---
def get_auto_analysis(ticker):
    try:
        symbol = f"{ticker.upper()}.CA"
        stock = yf.Ticker(symbol)
        df = stock.history(period="150d")
        df_now = stock.history(period="1d", interval="1m")
        if df.empty: return None
        
        p = df_now['Close'].iloc[-1] if not df_now.empty else df['Close'].iloc[-1]
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # المتوسطات للاتجاه
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        
        return {
            "p": p, "rsi": df['RSI'].iloc[-1],
            "ts": "صاعد 🟢" if p > ma10 else "هابط 🔴",
            "tm": "صاعد 🟢" if p > ma50 else "هابط 🔴",
            "prev": stock.info.get('previousClose', df['Close'].iloc[-2]),
            "vol": (df['Volume'].iloc[-1] * p) / 1_000_000
        }
    except: return None

st.markdown("<h1 style='text-align:center; color:white;'>🎯 EGX Ultimate Sniper</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثل ATQA أو MOED):", "").strip().upper()

if u_input:
    auto = get_auto_analysis(u_input)
    report_text = "" 
    
    if auto:
        p = auto['p']
        change = ((p - auto['prev']) / auto['prev']) * 100
        st.markdown(f"""
        <div class="report-card">
            <h3 style="margin:0;">💎 تقرير {u_input} الشامل</h3>
            <div class="price-val">{p:.3f}</div>
            <b style="color:{'green' if change > 0 else 'red'}; font-size:18px;">{change:+.2f}%</b>
            <p style="margin-top:5px;">RSI: {auto['rsi']:.1f} | سيولة: {auto['vol']:.2f}M</p>
            
            <div class="section-header">🔍 الاتجاهات</div>
            • قصير: {auto['ts']} | متوسط: {auto['tm']}
            
            <div class="section-header">🚀 الأهداف (المقاومات)</div>
            • هدف 1: {p*1.025:.3f} 🔷 | هدف 2: {p*1.050:.3f} 🔷
            
            <div class="section-header">🛡️ الدعوم</div>
            • دعم 1: {p*0.975:.3f} 🔸 | دعم 2: {p*0.950:.3f} 🔸
            
            <div class="section-header">🛑 وقف الخسارة</div>
            • {p*0.940:.3f} 🛑
        </div>
        """, unsafe_allow_html=True)
        
        report_text = f"📊 تحليل {u_input}:\n💰 السعر: {p:.3f}\n🚀 أهداف: {p*1.025:.3f} - {p*1.050:.3f}\n🛡️ دعوم: {p*0.975:.3f}\n🛑 وقف: {p*0.940:.3f}"

    # 2. لوحة التحليل اليدوي (الزرار الأبيض المنور)
    st.markdown("---")
    with st.expander(f"🛠️ لوحة التحليل اليدوي لـ {u_input} (إضافة بيانات خاصة)", expanded=not auto):
        st.markdown("<div class='manual-panel'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: m_price = st.number_input("السعر الآن:", format="%.3f", step=0.001, key="m1")
        with c2: m_high = st.number_input("أعلى اليوم:", format="%.3f", step=0.001, key="m2")
        with c3: m_low = st.number_input("أقل اليوم:", format="%.3f", step=0.001, key="m3")
        
        st.write("📈 **بيانات المستثمر والسيولة:**")
        col4, col5, col6 = st.columns(3)
        with col4: mh = st.number_input("أعلى سعر شهر:", format="%.3f", key="m4")
        with col5: v_today = st.number_input("سيولة اليوم:", format="%.2f", key="m5")
        with col6: v_avg = st.number_input("متوسط السيولة:", format="%.2f", key="m6")
        st.markdown("</div>", unsafe_allow_html=True)

        if m_price > 0 and m_high > 0:
            piv = (m_high + m_low + m_price) / 3
            r1_d = (2 * piv) - m_low
            s1_d = (2 * piv) - m_high
            
            st.markdown(f"""
            <div class="report-card" style="border-top-color: #00c853;">
                <h3>📊 نتيجة التحليل اليدوي لـ {u_input}</h3>
                <div class="price-val">{m_price:.3f}</div>
                <div class="section-header">🏹 أهداف المضارب</div>
                • مقاومة: {r1_d:.3f} 🔷 | دعم: {s1_d:.3f} 🔸
                <div class="section-header">📍 الارتكاز (Pivot)</div>
                • {piv:.3f}
            </div>
            """, unsafe_allow_html=True)
            report_text = f"🛠️ تحليل يدوي {u_input}:\n💰 السعر: {m_price:.3f}\n🚀 هدف: {r1_d:.3f}\n🛡️ دعم: {s1_d:.3f}\n📍 ارتكاز: {piv:.3f}"

    # صندوق النسخ
    if report_text:
        st.markdown(f"""
        <div class="whatsapp-box">
            <b>📱 نص التقرير الجاهز للنسخ:</b><br><br>
            {report_text.replace('\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)
        st.button("اضغط مطولاً على النص أعلاه للنسخ")

st.caption("EGX Pro Sniper v4.0 | 2026")
