import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS الاحترافي (زرار مودرن + تفتيح شامل) ---
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    
    /* تفتيح المدخلات اليدوية */
    label p, .stMarkdown p, .stExpander p { color: #ffffff !important; font-weight: bold !important; opacity: 1 !important; }
    input { background-color: #1e2732 !important; color: white !important; border: 1px solid #3498db !important; }

    /* تنسيق زرار الواتساب المودرن (خارج الحاوية) */
    .stButton>button {
        background: linear-gradient(90deg, #25D366, #128C7E) !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 15px !important;
        width: 100% !important;
        transition: 0.3s !important;
        box-shadow: 0 4px 15px rgba(37,211,102,0.3) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37,211,102,0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

ARABIC_DB = {"SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "TMGH": "طلعت مصطفى", "ATQA": "مصر الوطنية للصلب", "SWDY": "السويدي إليكتريك", "FWRY": "فوري", "BTFH": "بلتون"}

st.title("📊 Smart Stock Analyzer")
u_input = st.text_input("🔍 كود السهم (مثلاً TMGH):").upper().strip()

def build_safe_card(name, sym, p, hi, lo, cl, vol, piv, rs, ss):
    # منطق التوصية والاتجاه
    trend_short = "صاعد 📈" if p > piv else "هابط 📉"
    trend_med = "إيجابي 👍" if p > cl else "سلبي 👎"
    recommendation = "شراء (اختراق)" if p > piv else "مراقبة (دعم)"
    
    # 1. تصميم الكارت (بدون الزرار بالداخل لضمان العمل)
    card_html = f"""
    <div style="direction: rtl; font-family: sans-serif; background: #1e2732; border-radius: 15px; border: 1px solid #30363d; padding: 20px; color: white;">
        <h2 style="text-align: center; margin-bottom: 10px;">{name} ({sym})</h2>
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background: #3498db; padding: 5px 15px; border-radius: 20px; font-size: 14px; font-weight: bold;">{recommendation}</span>
        </div>

        <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
            <div style="text-align: center; background: #0d1117; padding: 10px; border-radius: 10px; flex: 1; margin: 0 5px; border: 1px solid #3d444d;">
                <div style="color: #8b949e; font-size: 12px;">قصير</div><div style="font-weight: bold;">{trend_short}</div>
            </div>
            <div style="text-align: center; background: #0d1117; padding: 10px; border-radius: 10px; flex: 1; margin: 0 5px; border: 1px solid #3d444d;">
                <div style="color: #8b949e; font-size: 12px;">متوسط</div><div style="font-weight: bold;">{trend_med}</div>
            </div>
            <div style="text-align: center; background: #0d1117; padding: 10px; border-radius: 10px; flex: 1; margin: 0 5px; border: 1px solid #3d444d;">
                <div style="color: #8b949e; font-size: 12px;">طويل</div><div style="font-weight: bold;">مستقر ⚖️</div>
            </div>
        </div>

        <div style="background: #0d1117; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #f1c40f; margin-bottom: 15px;">
            <span style="color: #f1c40f; font-weight: bold; font-size: 14px;">🟡 نقطة الارتكاز المحورية</span><br>
            <span style="font-size: 24px; font-weight: bold; color: white;">{piv:.3f}</span>
        </div>

        <div style="display: flex; justify-content: space-between; gap: 10px;">
            <div style="flex: 1; background: #161b22; padding: 15px; border-radius: 12px; border-right: 4px solid #3498db;">
                <div style="color: #3498db; font-weight: bold; margin-bottom: 8px;">🚀 المقاومات</div>
                <div style="color: white; line-height: 1.8;">م1: {rs[0]:.3f}<br>م2: {rs[1]:.3f}<br>م3: {rs[2]:.3f}</div>
            </div>
            <div style="flex: 1; background: #161b22; padding: 15px; border-radius: 12px; border-right: 4px solid #e74c3c;">
                <div style="color: #e74c3c; font-weight: bold; margin-bottom: 8px;">🛡️ الدعوم</div>
                <div style="color: white; line-height: 1.8;">د1: {ss[0]:.3f}<br>د2: {ss[1]:.3f}<br>د3: {ss[2]:.3f}</div>
            </div>
        </div>

        <div style="background: #0d1117; padding: 10px; border-radius: 10px; margin-top: 15px; border: 1px solid #30363d; font-size: 13px; text-align: center; color: #8b949e;">
            السعر: <b style="color:white">{p:.3f}</b> | أعلى: {hi:.3f} | أدنى: {lo:.3f} | أمس: {cl:.3f}
        </div>
    </div>
    """
    components.html(card_html, height=480, scrolling=False)

    # 2. زر الواتساب (باستخدام st.link_button لضمان عمله 100%)
    wa_msg = (f"🎯 تقرير: {name} ({sym})\n💰 السعر: {p:.3f}\n🟡 الارتكاز: {piv:.3f}\n"
              f"🟢 التوصية: {recommendation}\n📊 الاتجاه: {trend_short}\n"
              f"🚀 م1: {rs[0]:.3f} | 🛡️ د1: {ss[0]:.3f}\n📊 سيولة: {vol:.1f}M")
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
    
    st.link_button("📲 مشاركة التقرير الذكي عبر WhatsApp", wa_url)

# --- محرك البحث ---
found = False
if u_input:
    try:
        ticker = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        df = yf.Ticker(ticker).history(period="5d")
        if not df.empty:
            l = df.iloc[-1]
            p, hi, lo, cl = l["Close"], l["High"], l["Low"], df["Close"].iloc[-2]
            piv = (hi + lo + p) / 3
            rs = [(2*piv)-lo, piv+(hi-lo), hi+2*(piv-lo)]
            ss = [(2*piv)-hi, piv-(hi-lo), lo-2*(hi-piv)]
            build_safe_card(ARABIC_DB.get(u_input, "سهم متداول"), u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, piv, rs, ss)
            found = True
    except: pass

# --- المدخلات اليدوية ---
st.markdown("---")
st.subheader("🛠️ الإدخال اليدوي")
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("💵 السعر الآن", format="%.3f", key="p81")
with c2: hm = st.number_input("🔝 أعلى اليوم", format="%.3f", key="h81")
with c3: lm = st.number_input("📉 أقل اليوم", format="%.3f", key="l81")

with st.expander("📊 بيانات إضافية للرسالة"):
    cx, cy = st.columns(2)
    with cx: clm = st.number_input("↩️ إغلاق أمس", format="%.3f", key="c81")
    with cy: vm = st.number_input("💧 السيولة (M)", format="%.2f", key="v81")

if pm > 0 and not found:
    piv = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*piv)-lm if lm > 0 else pm*1.02, pm*1.04, pm*1.06]
    ss = [(2*piv)-hm if hm > 0 else pm*0.98, pm*0.96, pm*0.94]
    build_safe_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, piv, rs, ss)
