import streamlit as st
import urllib.parse

# إعداد الصفحة وتنسيق الألوان الناصعة جداً
st.set_page_config(page_title="EGX Manual Sniper v95", layout="centered")

st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    /* جعل الخطوط بيضاء ناصعة جداً */
    .stMarkdown p, label p, h1, h2, h3, span { color: #FFFFFF !important; font-weight: 900 !important; }
    input { background-color: #1e2732 !important; color: #FFFFFF !important; border: 2px solid #3498db !important; }
    .stNumberInput input { font-size: 22px !important; height: 50px !important; }
</style>
""", unsafe_allow_html=True)

st.title("🏹 قناص البورصة v95 🔥")
st.write("التحليل اليدوي 100% دقيق - أدخل أرقام الشاشة فوراً:")

# --- لوحة الإدخال اليدوي الأساسية (مفتوحة دائماً) ---
with st.container():
    c1, c2, c3 = st.columns(3)
    p = c1.number_input("السعر الآن", format="%.3f", step=0.001)
    hi = c2.number_input("أعلى سعر", format="%.3f", step=0.001)
    lo = c3.number_input("أقل سعر", format="%.3f", step=0.001)

if p > 0 and hi > 0:
    # الحسابات الفنية
    piv = (p + hi + lo) / 3
    s1 = (2 * piv) - hi
    r1 = (2 * piv) - lo
    
    st.markdown("---")
    
    # --- نظام الإشعارات الفوري (الرادار) ---
    # 1. إشارة دخول (أخضر فوسفوري)
    if p <= (s1 * 1.005):
        st.markdown(f"""
        <div style="background: #2ecc71; padding: 25px; border-radius: 15px; text-align: center; border: 4px solid #ffffff; margin-bottom: 20px;">
            <h1 style="color: #000000 !important; margin: 0; font-size: 40px;">🔥 فرصة دخول الآن 🔥</h1>
            <p style="color: #000000 !important; font-size: 22px; font-weight: bold;">السعر عند الدعم المثالي: {s1:.3f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 2. إشارة خروج/بيع (أحمر ناري)
    elif p >= (r1 * 0.995):
        st.markdown(f"""
        <div style="background: #e74c3c; padding: 25px; border-radius: 15px; text-align: center; border: 4px solid #ffffff; margin-bottom: 20px;">
            <h1 style="color: #ffffff !important; margin: 0; font-size: 40px;">🚀 إشارة بيع / جني أرباح 🚀</h1>
            <p style="color: #ffffff !important; font-size: 22px;">السهم وصل للمقاومة: {r1:.3f}</p>
        </div>
        """, unsafe_allow_html=True)

    # --- كارت التحليل الفخم ---
    st.markdown(f"""
    <div style="background: #1e2732; padding: 30px; border-radius: 20px; border: 2px solid #3498db; text-align: center;">
        <div style="background: #0d1117; padding: 20px; border-radius: 15px; margin-bottom: 25px; border: 1px solid #f1c40f;">
            <p style="color: #f1c40f !important; margin: 0; font-size: 20px;">🟡 نقطة الارتكاز (الميزان)</p>
            <h1 style="font-size: 60px; margin: 10px 0; color: #ffffff !important;">{piv:.3f}</h1>
        </div>
        
        <div style="display: flex; justify-content: space-between; gap: 15px;">
            <div style="flex: 1; background: #0d1117; padding: 20px; border-radius: 15px; border-bottom: 6px solid #e74c3c;">
                <p style="color: #e74c3c !important; margin: 0; font-size: 18px;">📉 منطقة الشراء</p>
                <h2 style="font-size: 35px; margin: 10px 0;">{s1:.3f}</h2>
            </div>
            <div style="flex: 1; background: #0d1117; padding: 20px; border-radius: 15px; border-bottom: 6px solid #2ecc71;">
                <p style="color: #2ecc71 !important; margin: 0; font-size: 18px;">📈 منطقة البيع</p>
                <h2 style="font-size: 35px; margin: 10px 0;">{r1:.3f}</h2>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # زر الواتساب
    st.markdown("<br>", unsafe_allow_html=True)
    msg = f"🎯 تحليل سهم فني:\n💰 السعر: {p:.3f}\n🟡 الارتكاز: {piv:.3f}\n🟢 شراء: {s1:.3f}\n🔴 بيع: {r1:.3f}"
    st.link_button("📲 مشاركة التوصية على WhatsApp", f"https://wa.me/?text={urllib.parse.quote(msg)}")

else:
    st.info("💡 أدخل (السعر وأعلى وأقل) لتفعيل الرادار وظهور الإشعارات فوراً.")

st.markdown("---")
st.caption("ملاحظة: هذا الكود يعمل يدوياً لضمان السرعة القصوى وتجنب تأخير المواقع.")
