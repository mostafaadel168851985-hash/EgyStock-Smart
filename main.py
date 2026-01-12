import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.parse
import streamlit.components.v1 as components

# إعداد الصفحة
st.set_page_config(page_title="EGX Ultimate Sniper", layout="centered")

# --- قاعدة بيانات الأسماء العربية الشاملة ---
EGX_DB = {
    "COMI": "البنك التجاري الدولي", "TMGH": "مجموعة طلعت مصطفى", "FWRY": "فوري",
    "SWDY": "السويدي إليكتريك", "ESRS": "حديد عز", "ABUK": "أبوقير للأسمدة",
    "AMOC": "أمو ك", "BTFH": "بلتون المالية", "SKPC": "سيدي كرير",
    "EKHO": "القابضة الكويتية", "ETEL": "المصرية للاتصالات", "JUFO": "جهينة",
    "CCAP": "القلعة", "ORAS": "أوراسكوم للإنشاء", "PHDC": "بالم هيلز"
}

# --- CSS التنسيق النهائي ---
st.markdown("""
<style>
    header, .main, .stApp { background-color: #0d1117 !important; }
    .stMarkdown p, label p { color: white !important; font-weight: bold; }
    input { background-color: #1e2732 !important; color: white !important; border: 1px solid #3498db !important; }
    .stButton>button {
        background: linear-gradient(90deg, #25D366, #128C7E) !important;
        color: white !important; width: 100%; border-radius: 0 0 15px 15px !important;
        margin-top: -25px !important; height: 50px; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏹 EGX Ultimate Sniper v86")
u_input = st.text_input("🔍 ادخل كود السهم (مثلاً TMGH):").upper().strip()

# مكان للإشعارات
alert_area = st.empty()

def build_ultimate_card(name, sym, p, hi, lo, cl, vol, piv, rs, ss):
    # 1. حساب المؤشرات (الرادار)
    strength = min(max(((p - piv) / piv) * 100 * 5, -100), 100)
    risk = "منخفضة ✅" if p < piv * 1.02 else "متوسطة ⚠️" if p < rs[0] else "عالية 🚨"
    
    # 2. نظام التنبيهات (الرادار)
    if p <= ss[0] * 1.005:
        alert_area.error(f"🚨 تنبيه رادار: {name} عند منطقة دعم قوية ({ss[0]:.3f})")
        st.toast(f"فرصة دخول في {name}", icon="💰")
    elif p >= rs[0] * 0.995:
        alert_area.success(f"🚀 تنبيه رادار: {name} يخترق المقاومة ({rs[0]:.3f})")
        st.toast(f"انفجار سعري في {name}", icon="🔥")

    # 3. تصميم الكارت
    card_html = f"""
    <div style="direction: rtl; font-family: sans-serif; background: #1e2732; border-radius: 15px 15px 0 0; border: 1px solid #30363d; padding: 20px; color: white;">
        <div style="text-align: center; border-bottom: 1px solid #3d444d; padding-bottom: 10px; margin-bottom: 15px;">
            <h2 style="margin: 0; color: #3498db;">{name} <small style="font-size:14px; color:#8b949e;">({sym})</small></h2>
        </div>

        <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
            <div style="text-align: center;">
                <div style="color: #8b949e; font-size: 12px;">السعر اللحظي</div>
                <div style="font-size: 24px; font-weight: bold; color: #2ecc71;">{p:.3f}</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #8b949e; font-size: 12px;">قوة الزخم</div>
                <div style="font-size: 24px; font-weight: bold; color: #f1c40f;">{strength:.1f}%</div>
            </div>
        </div>

        <div style="background: #0d1117; padding: 15px; border-radius: 12px; border: 1px solid #f1c40f; text-align: center; margin-bottom: 15px;">
            <div style="color: #f1c40f; font-size: 13px; font-weight: bold;">🟡 نقطة الارتكاز المحورية</div>
            <div style="font-size: 26px; font-weight: bold;">{piv:.3f}</div>
        </div>

        <div style="display: flex; justify-content: space-between; gap: 10px; margin-bottom: 15px;">
            <div style="flex: 1; background: #161b22; padding: 10px; border-radius: 10px; border-right: 4px solid #3498db;">
                <div style="color: #3498db; font-size: 12px;">الهدف (م1)</div>
                <div style="font-weight: bold;">{rs[0]:.3f}</div>
            </div>
            <div style="flex: 1; background: #161b22; padding: 10px; border-radius: 10px; border-right: 4px solid #e74c3c;">
                <div style="color: #e74c3c; font-size: 12px;">الوقف (د1)</div>
                <div style="font-weight: bold;">{ss[0]:.3f}</div>
            </div>
        </div>

        <div style="background: #0d1117; padding: 10px; border-radius: 10px; font-size: 12px; color: #8b949e; display: flex; justify-content: space-between;">
            <span>🔝 أعلى: {hi:.3f}</span>
            <span>📉 أدنى: {lo:.3f}</span>
            <span>📊 سيولة: {vol:.1f}M</span>
        </div>
        <div style="text-align: center; font-size: 11px; margin-top: 10px; color: #8b949e;">
            المخاطرة: <span style="color: white;">{risk}</span> | إغلاق أمس: {cl:.3f}
        </div>
    </div>
    """
    components.html(card_html, height=480)

    # 4. رابط الواتساب
    wa_msg = (f"🎯 تقرير {name} ({sym})\n💰 سعرنا: {p:.3f}\n🟡 ارتكاز: {piv:.3f}\n"
              f"🚀 هدف: {rs[0]:.3f}\n🛡️ وقف: {ss[0]:.3f}\n📊 زخم: {strength:.1f}%")
    st.link_button("📲 مشاركة التقرير الفني عبر WhatsApp", f"https://wa.me/?text={urllib.parse.quote(wa_msg)}")

# --- تنفيذ المحرك ---
if u_input:
    try:
        ticker = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        stock = yf.Ticker(ticker)
        df = stock.history(period="5d")
        if not df.empty:
            l = df.iloc[-1]
            p = stock.fast_info['last_price'] if 'last_price' in stock.fast_info else l["Close"]
            hi, lo, cl = l["High"], l["Low"], df["Close"].iloc[-2]
            piv = (hi + lo + p) / 3
            rs = [(2*piv)-lo, piv+(hi-lo), hi+2*(piv-lo)]
            ss = [(2*piv)-hi, piv-(hi-lo), lo-2*(hi-piv)]
            name = EGX_DB.get(u_input, stock.info.get('longName', u_input))
            build_ultimate_card(name, u_input, p, hi, lo, cl, (l['Volume']*p)/1e6, piv, rs, ss)
    except:
        st.warning("⚠️ حاول كتابة الكود مرة أخرى أو استخدم الإدخال اليدوي")

# --- الإدخال اليدوي الكامل ---
st.markdown("---")
with st.expander("🛠️ الإدخال اليدوي (بياناتك الخاصة)"):
    c1, c2, c3 = st.columns(3)
    pm = c1.number_input("السعر الآن", format="%.3f", key="man_p")
    hm = c2.number_input("أعلى سعر", format="%.3f", key="man_h")
    lm = c3.number_input("أقل سعر", format="%.3f", key="man_l")
    cx, cy = st.columns(2)
    clm = cx.number_input("إغلاق أمس", format="%.3f", key="man_c")
    vlm = cy.number_input("السيولة (M)", format="%.1f", key="man_v")
    
    if pm > 0:
        piv_m = (hm + lm + pm) / 3
        rs_m = [(2*piv_m)-lm, piv_m+(hm-lm)]
        ss_m = [(2*piv_m)-hm, piv_m-(hm-lm)]
        build_ultimate_card("تحليل يدوي", u_input if u_input else "MANUAL", pm, hm, lm, clm, vlm, piv_m, rs_m, ss_m)
