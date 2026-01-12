import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

# 1. إعدادات المظهر الاحترافي
st.set_page_config(page_title="EGX Sniper v104", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: bold; }
    input { background-color: #1e2732 !important; color: #FFFFFF !important; border: 2px solid #3498db !important; }
    
    /* تنسيق كارت التقرير (شبه التليجرام) */
    .report-card {
        background: #ffffff; color: #000000; padding: 25px; 
        border-radius: 20px; border: 4px solid #3498db; font-family: 'Arial';
    }
    .report-card h3 { color: #1e2732 !important; text-align: center; border-bottom: 2px solid #3498db; }
    
    /* زرار الواتساب Modern */
    .wa-btn {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important; padding: 18px; border-radius: 15px;
        text-decoration: none; font-weight: bold; margin-top: 20px;
        box-shadow: 0 4px 15px rgba(18,140,126,0.3);
    }
</style>
""", unsafe_allow_html=True)

# 2. دالة عرض التقرير المتكاملة
def generate_full_report(title, p, hi, lo):
    # الحسابات الفنية
    piv = (p + hi + lo) / 3
    s1, s2 = (2 * piv) - hi, piv - (hi - lo)
    r1, r2 = (2 * piv) - lo, piv + (hi - lo)
    stop_loss = s2 * 0.99

    # الإشعارات اللحظية
    if p <= (s1 * 1.005):
        st.success(f"🔥 فرصة دخول قوية: السهم عند الدعم {s1:.2f}")
    
    # عرض التقرير (تصميم التليجرام)
    st.markdown(f"""
    <div class="report-card">
        <h3>💎 التحليل الشامل لـ {title}</h3>
        <p>💰 <b>السعر المعتمد:</b> {p:.2f}</p>
        <p>💧 <b>نبض السيولة:</b> طبيعية ⚖️</p>
        <p>📢 <b>التوصية:</b> مراقبة عند الدعوم ⚖️</p>
        <hr>
        <p>🔍 <b>الأسباب الفنية:</b></p>
        <p>✅ السعر يتفاعل مع مناطق الارتكاز</p>
        <hr>
        <p style="color: #2ecc71;">🚀 <b>مستويات المقاومة:</b></p>
        <p>🎯 هدف 1: {r1:.2f} | هدف 2: {r2:.2f}</p>
        <hr>
        <p style="color: #e67e22;">🛡️ <b>مستويات الدعم:</b></p>
        <p>🔸 دعم 1: {s1:.2f} | دعم 2: {s2:.2f}</p>
        <hr>
        <p style="color: #e74c3c;">🛑 <b>وقف خسارة: {stop_loss:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # زر الواتساب المودرن
    wa_msg = f"💎 تحليل {title}:\n💰 السعر: {p:.2f}\n🎯 أهداف: {r1:.2f} - {r2:.2f}\n🛡️ دعوم: {s1:.2f} - {s2:.2f}\n🛑 وقف: {stop_loss:.2f}"
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_msg)}" class="wa-btn">📲 مشاركة عبر واتساب</a>', unsafe_allow_html=True)

# 3. الواجهة الرئيسية
st.title("🏹 رادار قناص البورصة v104")

tab1, tab2 = st.tabs(["📡 البحث الآلي", "🛠️ التحليل اليدوي"])

with tab1:
    u_input = st.text_input("ادخل كود السهم (مثل ATQA):").upper().strip()
    if u_input:
        try:
            stock = yf.Ticker(f"{u_input}.CA")
            df = stock.history(period="1d")
            if not df.empty:
                p, hi, lo = df['Close'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1]
                generate_full_report(u_input, p, hi, lo)
            else:
                st.error("⚠️ لم نجد داتا حالياً.. جرب اليدوي.")
        except:
            st.error("❌ عطل فني في جلب البيانات.")

with tab2:
    st.info("حط أرقام الشاشة هنا وهيطلعلك التقرير فوراً")
    c1, c2, c3 = st.columns(3)
    p_in = c1.number_input("السعر الآن", format="%.2f")
    h_in = c2.number_input("أعلى سعر", format="%.2f")
    l_in = c3.number_input("أقل سعر", format="%.2f")
    
    if p_in > 0:
        generate_full_report("تحليل يدوي", p_in, h_in, l_in)
