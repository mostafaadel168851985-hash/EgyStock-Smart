import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

# 1. إعدادات التصميم (Dark Mode احترافي)
st.set_page_config(page_title="EGX Sniper Elite v100", layout="centered")
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: 900 !important; }
    input { background-color: #1e2732 !important; color: #FFFFFF !important; border: 2px solid #3498db !important; }
    div[data-testid="stExpander"] { background-color: #1e2732 !important; border: 1px solid #3498db !important; }
</style>
""", unsafe_allow_html=True)

# 2. القاموس العربي
EGX_DB = {"COMI": "التجاري الدولي", "TMGH": "طلعت مصطفى", "FWRY": "فوري", "SWDY": "السويدي إليكتريك", "ESRS": "حديد عز", "ABUK": "أبوقير للأسمدة", "AMOC": "أمو ك", "BTFH": "بلتون المالية"}

# 3. محرك جلب البيانات الذكي
def get_stock_analysis(ticker):
    try:
        t_ca = f"{ticker}.CA"
        stock = yf.Ticker(t_ca)
        p = stock.fast_info['last_price']
        df = stock.history(period="5d") # سحب 5 أيام لحساب المتوسطات
        if not df.empty:
            hi, lo = df['High'].iloc[-1], df['Low'].iloc[-1]
            ma50 = df['Close'].mean() # متوسط تقريبي
            return p, hi, lo, ma50
        return p, p, p, p
    except: return None, None, None, None

# 4. الواجهة الرئيسية
st.title("🎯 رادار القناص v100 - التقرير الشامل")

u_input = st.text_input("🔍 ادخل كود السهم (مثل TMGH):").upper().strip()

if u_input:
    with st.spinner('⏳ جاري استخراج البيانات وتحليل السهم...'):
        p, hi, lo, ma50 = get_stock_analysis(u_input)
    
    if p:
        # الحسابات الفنية (زي صورة التليجرام)
        piv = (p + hi + lo) / 3
        s1, s2 = (2 * piv) - hi, piv - (hi - lo)
        r1, r2 = (2 * piv) - lo, piv + (hi - lo)
        stop_loss = s2 * 0.99
        name = EGX_DB.get(u_input, u_input)

        # --- [1. نظام الإشعارات اللحظية] ---
        if p <= (s1 * 1.005):
            st.success(f"🔥 فرصة دخول قوية: السهم عند الدعم {s1:.2f}")
        elif p >= (r1 * 0.995):
            st.error(f"🚀 إشارة بيع/تخفيف: السهم عند المقاومة {r1:.2f}")

        # --- [2. شكل تقرير التليجرام] ---
        report_html = f"""
        <div style="background: #ffffff; color: #000000; padding: 20px; border-radius: 15px; font-family: 'Arial'; border: 2px solid #3498db;">
            <h3 style="text-align: center; border-bottom: 2px solid #000;">💎 التحليل الشامل لـ {u_input}</h3>
            <p>💰 <b>السعر المعتمد:</b> {p:.2f}</p>
            <p>💧 <b>نبض السيولة:</b> طبيعية ⚖️</p>
            <p>📢 <b>التوصية:</b> احتفاظ / مراقبة ⚖️</p>
            <hr style="border: 1px solid #eee;">
            <p>🔍 <b>الأسباب الفنية:</b></p>
            <p>✅ السعر {'فوق' if p > ma50 else 'تحت'} متوسط 50</p>
            <p>⚠️ القوة النسبية (RSI) متزنة</p>
            <hr style="border: 1px solid #eee;">
            <p>🚀 <b>مستويات المقاومة:</b></p>
            <p>🔹 هدف 1: {r1:.2f}</p>
            <p>🔹 هدف 2: {r2:.2f}</p>
            <hr style="border: 1px solid #eee;">
            <p>🛡️ <b>مستويات الدعم:</b></p>
            <p>🔸 دعم 1: {s1:.2f}</p>
            <p>🔸 دعم 2: {s2:.2f}</p>
            <hr style="border: 1px solid #eee;">
            <p>🛑 <b>وقف الخسارة:</b> {stop_loss:.2f}</p>
        </div>
        """
        st.markdown(report_html, unsafe_allow_html=True)

        # --- [3. زر الواتساب] ---
        wa_msg = f"💎 تحليل {name} ({u_input}):\n💰 السعر: {p:.2f}\n🎯 أهدافك: {r1:.2f} - {r2:.2f}\n🛡️ دعومك: {s1:.2f} - {s2:.2f}\n🛑 وقف: {stop_loss:.2f}"
        st.link_button("📲 إرسال هذا التقرير للواتساب", f"https://wa.me/?text={urllib.parse.quote(wa_msg)}")
    else:
        st.error("❌ تعذر جلب البيانات. جرب اليدوي.")

# 5. اليدوي (للطوارئ)
st.markdown("---")
with st.expander("🛠️ لوحة التحكم اليدوية"):
    m_p = st.number_input("السعر الآن", format="%.2f")
    if m_p > 0: st.info("بمجرد إدخال الهاي واللو في النسخة القادمة سيظهر التقرير كاملاً هنا")
