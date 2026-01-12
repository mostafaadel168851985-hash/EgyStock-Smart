import streamlit as st
import urllib.parse

# 1. تصميم الواجهة (Dark & Professional)
st.set_page_config(page_title="EGX Smart Analyst v102", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: bold !important; }
    input { background-color: #1e2732 !important; color: #FFFFFF !important; border: 2px solid #3498db !important; }
    
    /* زرار واتساب Modern and Smart */
    .wa-link {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important; padding: 18px; border-radius: 15px;
        font-size: 20px; font-weight: bold; text-decoration: none;
        margin-top: 25px; box-shadow: 0 10px 20px rgba(18, 140, 126, 0.3);
        transition: 0.3s;
    }
    .wa-link:hover { transform: translateY(-3px); box-shadow: 0 15px 25px rgba(18, 140, 126, 0.4); }
</style>
""", unsafe_allow_html=True)

st.title("🎯 مستشار البورصة اللحظي v102")
st.write("أدخل بيانات السهم من الشاشة الآن للحصول على التقرير والإشعارات:")

# 2. لوحة الإدخال الذكية
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1: p = st.number_input("السعر الآن", format="%.2f", step=0.01)
    with col2: hi = st.number_input("أعلى سعر", format="%.2f", step=0.01)
    with col3: lo = st.number_input("أقل سعر", format="%.2f", step=0.01)
    u_name = st.text_input("اسم السهم (اختياري)", placeholder="مثلاً: عتاقة")

if p > 0 and hi > 0 and lo > 0:
    # الحسابات الفنية الدقيقة
    piv = (p + hi + lo) / 3
    s1, s2 = (2 * piv) - hi, piv - (hi - lo)
    r1, r2 = (2 * piv) - lo, piv + (hi - lo)
    stop_loss = s2 * 0.98
    
    st.markdown("---")
    
    # 3. نظام الإشعارات الذكي
    if p <= (s1 * 1.005):
        st.success(f"🔥 إشارة دخول: السهم عند منطقة دعم قوية ({s1:.2f})")
    elif p >= (r1 * 0.995):
        st.error(f"🚀 إشارة بيع: السهم وصل لمنطقة مستهدف اللحظي ({r1:.2f})")
    else:
        st.info("⚖️ السهم في منطقة تداول عرضية - راقب الدعوم")

    # 4. كارت التقرير (شكل التليجرام الاحترافي)
    st.markdown(f"""
    <div style="background: #ffffff; color: #000000; padding: 30px; border-radius: 20px; border: 4px solid #3498db;">
        <h2 style="text-align: center; color: #1e2732; border-bottom: 3px solid #3498db; padding-bottom: 10px;">💎 تقرير الأداء اللحظي</h2>
        <p style="font-size: 18px;">📊 <b>السهم:</b> {u_name if u_name else 'سهم مختار'}</p>
        <p style="font-size: 18px;">💰 <b>السعر الحالي:</b> {p:.2f}</p>
        <hr style="border: 0.5px solid #ddd;">
        <h4 style="color: #2ecc71;">🚀 مستويات المستهدفات:</h4>
        <p>🎯 هدف أول (مقاومة 1): <b>{r1:.2f}</b></p>
        <p>🎯 هدف ثاني (مقاومة 2): <b>{r2:.2f}</b></p>
        <hr style="border: 0.5px solid #ddd;">
        <h4 style="color: #e67e22;">🛡️ مستويات الأمان:</h4>
        <p>🔸 دعم أول: <b>{s1:.2f}</b></p>
        <p>🔸 دعم ثاني: <b>{s2:.2f}</b></p>
        <hr style="border: 0.5px solid #ddd;">
        <p style="color: #e74c3c; font-size: 20px;">🛑 <b>وقف خسارة فوري: {stop_loss:.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)

    # 5. زرار الواتساب Modern & Smart
    msg = f"💎 تحليل سهم {u_name}:\n💰 السعر: {p:.2f}\n🎯 أهداف: {r1:.2f} - {r2:.2f}\n🛡️ دعوم: {s1:.2f} - {s2:.2f}\n🛑 وقف: {stop_loss:.2f}"
    st.markdown(f'''
        <a href="https://wa.me/?text={urllib.parse.quote(msg)}" class="wa-link">
            <span>💬 إرسال التقرير الذكي عبر واتساب</span>
        </a>
    ''', unsafe_allow_html=True)

else:
    st.warning("💡 من فضلك أدخل السعر وأعلى وأقل سعر من شاشة التداول لإنشاء التقرير فوراً.")
