import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

st.set_page_config(page_title="EGX Sniper v91", layout="wide")

# --- تنسيق الألوان والفونتات (أبيض ناصع) ---
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3 { color: #ffffff !important; font-weight: bold !important; }
    input { background-color: #1e2732 !important; color: #ffffff !important; border: 2px solid #3498db !important; }
    div[data-testid="stExpander"] { background-color: #1e2732 !important; border: 1px solid #3498db !important; }
    .stAlert { background-color: #1e2732 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

st.title("🏹 رادار قناص البورصة المصرية")

# --- القائمة اللي الرادار بيفحصها لوحده ---
WATCHLIST = ["COMI.CA", "TMGH.CA", "FWRY.CA", "SWDY.CA", "ESRS.CA", "ABUK.CA", "BTFH.CA", "AMOC.CA", "ATQA.CA"]

# --- محرك رادار الفرص ---
def check_signals():
    signals = []
    try:
        # بنجيب البيانات بطريقة أخف عشان ياهو ميهنجش
        df = yf.download(WATCHLIST, period="1d", interval="5m", progress=False)
        for ticker in WATCHLIST:
            try:
                p = df['Close'][ticker].iloc[-1]
                hi = df['High'][ticker].max()
                lo = df['Low'][ticker].min()
                piv = (hi + lo + p) / 3
                s1 = (2 * piv) - hi
                
                # التنبيه اللي أنت عايزه (لو قرب من الدعم بـ 0.5% فقط)
                if p <= (s1 * 1.005): 
                    signals.append({"sym": ticker.replace(".CA", ""), "price": p, "s1": s1})
            except: continue
        return signals
    except: return []

# --- عرض "منبه الدخول" ---
st.subheader("🔥 فرص دخول قوية الآن (عند الدعم)")
current_signals = check_signals()

if current_signals:
    for sig in current_signals:
        st.error(f"⚠️ إشارة دخول صريحة: سهم {sig['sym']} لمس منطقة الدعم الآن! ({sig['s1']:.3f})")
else:
    st.info("🔎 الرادار يبحث.. لا توجد أسهم عند الدعم حالياً. (جرب تحديث الصفحة بعد قليل)")

# --- التحليل التفصيلي ---
st.markdown("---")
st.subheader("🔍 تحليل سهم محدد")
u_input = st.text_input("ادخل كود السهم (مثلاً TMGH):").upper().strip()

if u_input:
    try:
        t_code = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        s_data = yf.download(t_code, period="1d", interval="1m", progress=False)
        if not s_data.empty:
            p_val = s_data['Close'].iloc[-1]
            hi_val = s_data['High'].max()
            lo_val = s_data['Low'].min()
            piv_val = (hi_val + lo_val + p_val) / 3
            s1_val = (2 * piv_val) - hi_val
            r1_val = (2 * piv_val) - lo_val
            
            # شكل الكارت الاحترافي بالألوان الواضحة
            st.markdown(f"""
            <div style="background: #1e2732; padding: 20px; border-radius: 15px; border: 2px solid #3498db; text-align: center;">
                <h2 style="color:#ffffff; margin-bottom:15px;">{u_input}</h2>
                <div style="background: #0d1117; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <p style="color:#3498db; margin:0;">السعر اللحظي</p>
                    <h3 style="margin:0; font-size:32px; color:#2ecc71;">{p_val:.3f}</h3>
                </div>
                <div style="display: flex; justify-content: space-between; gap: 10px;">
                    <div style="flex:1; background:#0d1117; padding:10px; border-radius:8px; border-bottom:4px solid #e74c3c;">
                        <p style="color:#e74c3c; margin:0; font-size:14px;">منطقة الدخول (د1)</p><b>{s1_val:.3f}</b>
                    </div>
                    <div style="flex:1; background:#0d1117; padding:10px; border-radius:8px; border-bottom:4px solid #2ecc71;">
                        <p style="color:#2ecc71; margin:0; font-size:14px;">منطقة البيع (م1)</p><b>{r1_val:.3f}</b>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.warning("⚠️ ياهو فاينانس متأخر، استخدم الإدخال اليدوي فوراً.")

# --- الإدخال اليدوي المحدث ---
st.markdown("---")
with st.expander("🛠️ إدخال يدوي (أسرع حل وقت الجلسة)"):
    m_p = st.number_input("السعر الآن من الشاشة", format="%.3f")
    m_h = st.number_input("أعلى سعر النهاردة", format="%.3f")
    m_l = st.number_input("أقل سعر النهاردة", format="%.3f")
    if m_p > 0 and m_h > 0:
        m_piv = (m_p + m_h + m_l) / 3
        st.success(f"الارتكاز: {m_piv:.3f} | منطقة الشراء: {(2*m_piv)-m_h:.3f}")
