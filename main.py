import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse

st.set_page_config(page_title="EGX Sniper Radar", layout="wide")

# --- تنسيق الألوان والفونتات (أبيض ناصع) ---
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p, h1, h2, h3 { color: #ffffff !important; font-weight: bold !important; }
    .stAlert { border-radius: 10px !important; }
    div[data-testid="stExpander"] { background-color: #1e2732 !important; border: 1px solid #3498db !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 رادار صيد الفرص (EGX Sniper)")

# --- قائمة الأسهم اللي البرنامج هيراقبها تلقائياً ---
# تقدر تزود أي سهم في القائمة دي
WATCHLIST = ["COMI.CA", "TMGH.CA", "FWRY.CA", "SWDY.CA", "ESRS.CA", "ABUK.CA", "BTFH.CA", "AMOC.CA", "SKPC.CA"]

# --- محرك البحث والرادار ---
def start_radar():
    st.subheader("🕵️ جاري فحص السوق الآن...")
    found_opportunities = []
    
    # جلب البيانات لكل القائمة مرة واحدة لتوفير الوقت
    try:
        data = yf.download(WATCHLIST, period="2d", interval="1d", progress=False)
        
        for ticker in WATCHLIST:
            try:
                # حساب السعر والدعم لكل سهم
                current_price = data['Close'][ticker].iloc[-1]
                high = data['High'][ticker].iloc[-1]
                low = data['Low'][ticker].iloc[-1]
                prev_close = data['Close'][ticker].iloc[-2]
                
                pivot = (high + low + current_price) / 3
                support1 = (2 * pivot) - high
                
                # شرط "فرصة الدخول": السعر قريب من الدعم بنسبة 1% أو أقل منه
                if current_price <= (support1 * 1.01):
                    found_opportunities.append({
                        "ticker": ticker.replace(".CA", ""),
                        "price": current_price,
                        "support": support1,
                        "pivot": pivot
                    })
            except:
                continue
                
        return found_opportunities
    except:
        st.error("تعذر جلب بيانات الرادار، تأكد من الاتصال بالإنترنت.")
        return []

# --- عرض النتائج ---
opportunities = start_radar()

if opportunities:
    st.success(f"✅ تم العثور على {len(opportunities)} سهم في منطقة دخول جيدة!")
    
    # عرض الفرص في كروت مريحة للعين
    cols = st.columns(len(opportunities) if len(opportunities) < 4 else 3)
    for i, opp in enumerate(opportunities):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: #1e2732; padding: 20px; border-radius: 15px; border-top: 5px solid #2ecc71; margin-bottom: 20px;">
                <h3 style="margin:0; color:#2ecc71;">{opp['ticker']}</h3>
                <p style="margin:5px 0;">السعر: <b style="font-size:20px;">{opp['price']:.3f}</b></p>
                <p style="margin:5px 0; color:#e74c3c;">الدعم (د1): {opp['support']:.3f}</p>
                <hr style="border-color:#3d444d;">
                <p style="font-size:12px; color:#8b949e;">السعر الآن مثالي للدخول (قرب الدعم)</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("🔎 السوق حالياً يتداول أعلى من مناطق الدعم. لا توجد فرص دخول "آمنة" في القائمة الآن.")

# --- قسم البحث اليدوي المعتاد (عشان لو عايز تحلل سهم مش في الرادار) ---
st.markdown("---")
st.subheader("🔍 تحليل سهم محدد")
u_input = st.text_input("ادخل كود السهم (مثلاً ATQA):").upper().strip()

if u_input:
    # (هنا بنحط نفس كود التحليل بتاعنا اللي فات للسهم المنفرد)
    st.write(f"جاري تحليل {u_input}...")
    # ... (باقي كود الكارت الاحترافي والواتساب)
