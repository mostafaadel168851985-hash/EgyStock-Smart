import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

st.set_page_config(page_title="EGX Opportunities Radar", layout="wide")

# --- إصلاح الألوان والفونطات (أبيض ناصع) ---
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3, .stText { color: #ffffff !important; font-weight: bold !important; }
    input { background-color: #1e2732 !important; color: #ffffff !important; border: 2px solid #3498db !important; }
    div[data-testid="stExpander"] { background-color: #1e2732 !important; border: 1px solid #3498db !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 رادار صيد الفرص الذكي")

# --- قائمة المراقبة (تقدر تزود فيها براحتك) ---
WATCHLIST = ["COMI.CA", "TMGH.CA", "FWRY.CA", "SWDY.CA", "ESRS.CA", "ABUK.CA", "BTFH.CA", "AMOC.CA", "ATQA.CA"]

# --- محرك البحث عن فرص الدعم ---
def get_market_opportunities():
    opps = []
    try:
        # جلب البيانات لأهم الأسهم مرة واحدة
        df = yf.download(WATCHLIST, period="2d", interval="1d", progress=False)
        for ticker in WATCHLIST:
            try:
                p = df['Close'][ticker].iloc[-1]
                hi = df['High'][ticker].iloc[-1]
                lo = df['Low'][ticker].iloc[-1]
                piv = (hi + lo + p) / 3
                s1 = (2 * piv) - hi
                
                # شرط الإشارة: السعر قريب من الدعم أو لمسه
                if p <= (s1 * 1.01):
                    opps.append({"sym": ticker.replace(".CA", ""), "price": p, "s1": s1})
            except: continue
        return opps
    except: return []

# --- عرض قسم التنبيهات (الأسهم اللي في منطقة دعم) ---
st.subheader("⚠️ الأسهم في منطقة دخول الآن (عند الدعم)")
live_opps = get_market_opportunities()

if live_opps:
    cols = st.columns(len(live_opps) if len(live_opps) < 4 else 3)
    for i, item in enumerate(live_opps):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: #1e2732; padding: 15px; border-radius: 10px; border-right: 5px solid #2ecc71; margin-bottom: 10px;">
                <h3 style="color:#2ecc71; margin:0;">{item['sym']}</h3>
                <p style="margin:5px 0;">السعر: {item['price']:.3f}</p>
                <p style="margin:0; font-size:12px; color:#f1c40f;">الدعم الحالي: {item['s1']:.3f}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("🔎 لا توجد أسهم من القائمة عند مناطق دعم حالياً.")

# --- قسم التحليل الفردي (الكارت المعتاد) ---
st.markdown("---")
st.subheader("🔍 تحليل سهم محدد بالتفصيل")
u_input = st.text_input("ادخل كود السهم (مثلاً TMGH):").upper().strip()

if u_input:
    try:
        t_code = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        s_data = yf.download(t_code, period="5d", progress=False)
        if not s_data.empty:
            l = s_data.iloc[-1]
            p_val = l["Close"]
            hi_val, lo_val = l["High"], l["Low"]
            piv_val = (hi_val + lo_val + p_val) / 3
            s1_val = (2 * piv_val) - hi_val
            r1_val = (2 * piv_val) - lo_val
            
            st.markdown(f"""
            <div style="background: #1e2732; padding: 25px; border-radius: 15px; border: 2px solid #3498db; text-align: center;">
                <h2 style="color:white; margin-bottom:15px;">{u_input}</h2>
                <div style="display: flex; justify-content: space-around; background: #0d1117; padding: 15px; border-radius: 10px;">
                    <div><p style="color:#3498db; margin:0;">السعر</p><h3 style="margin:0;">{p_val:.3f}</h3></div>
                    <div><p style="color:#f1c40f; margin:0;">الارتكاز</p><h3 style="margin:0;">{piv_val:.3f}</h3></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 20px; gap: 10px;">
                    <div style="flex:1; background:#0d1117; padding:10px; border-radius:8px; border-bottom:3px solid #e74c3c;">
                        <p style="color:#e74c3c; margin:0;">الدعم (شراء)</p><b>{s1_val:.3f}</b>
                    </div>
                    <div style="flex:1; background:#0d1117; padding:10px; border-radius:8px; border-bottom:3px solid #2ecc71;">
                        <p style="color:#2ecc71; margin:0;">المقاومة (بيع)</p><b>{r1_val:.3f}</b>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.error("تعذر جلب بيانات السهم.")

# --- الإدخال اليدوي ---
st.markdown("---")
with st.expander("🛠️ الإدخال اليدوي (إذا كانت البيانات متأخرة)"):
    m_p = st.number_input("السعر الآن", format="%.3f")
    m_h = st.number_input("أعلى اليوم", format="%.3f")
    m_l = st.number_input("أقل اليوم", format="%.3f")
    if m_p > 0:
        m_piv = (m_p + m_h + m_l) / 3
        st.info(f"الارتكاز المحسوب يدوياً: {m_piv:.3f}")
