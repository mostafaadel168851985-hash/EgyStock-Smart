import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper v40", layout="centered")

# --- CSS التنسيق (شكل التليجرام الصافي) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        margin: 15px auto; line-height: 1.6;
    }
    .separator { border-top: 1px solid #333; margin: 15px 0; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 17px; margin-bottom: 5px; }
    .info-line { margin: 10px 0; font-size: 16px; display: flex; justify-content: space-between; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 12px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- القاموس المستخرج من ملفك الـ PDF بالظبط ---
ARABIC_NAMES = {
    "AALR": "العامة لاستصلاح الأراضي والتنمية",
    "ABUK": "أبو قير للأسمدة والصناعات الكيماوية",
    "ACAMD": "الشركة العربية لإدارة وتطوير الأصول",
    "ACAP": "ايه كابيتال القابضة",
    "ACGC": "العربية لحليج الأقطان",
    "ADIB": "مصرف أبو ظبي الإسلامي - مصر",
    "AFDI": "الأهلي للتنمية والاستثمار",
    "ALCN": "الاسكندرية لتداول الحاويات والبضائع",
    "AMOC": "الإسكندرية للزيوت المعدنية - أموك",
    "ANFI": "الإسكندرية للخدمات الطبية",
    "ARCC": "العربية للأسمنت",
    "ASCM": "أسيك للتعدين - أسكوم",
    "ATQA": "مصر الوطنية للصلب - عتاقة",
    "AUTO": "جي بي أوتو",
    "BINV": "بي انفستمنتس القابضة",
    "BTFH": "بلتون المالية القابضة",
    "COMI": "البنك التجاري الدولي (مصر)",
    "DAPH": "المطورون العرب القابضة",
    "DICE": "دايس للملابس الجاهزة",
    "EAST": "الشرقية - ايسترن كومباني",
    "EKHO": "القابضة المصرية الكويتية",
    "ETEL": "المصرية للاتصالات",
    "FWRY": "فوري لتكنولوجيا البنوك",
    "HELI": "مصر الجديدة للإسكان والتعمير",
    "JUFO": "جهينة للصناعات الغذائية",
    "MFOT": "مصر لإنتاج الأسمدة - موبكو",
    "MOED": "المصرية لنظم التعليم الحديث",
    "ORAS": "أوراسكوم كونستراكشون",
    "PHDC": "بالم هيلز للتعمير",
    "SWDY": "السويدي إليكتريك",
    "TMGH": "مجموعة طلعت مصطفى القابضة",
    "UEGC": "الصعيد العامة للمقاولات والاستثمار",
    "UNIP": "يونيفرسال لصناعة مواد التعبئة",
    "UNIT": "المتحدة للاسكان والتعمير",
    "UPMS": "الاتحاد الصيدلي للخدمات الطبية"
}

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز من الملف (مثلاً ABUK أو UEGC):").upper().strip()

def build_telegram_report(name, symbol, price, vol, rsi, ma50=None, close_prev=None, m_high=None, is_auto=True):
    liq_status = "طبيعية ⚖️" if vol > 10 else "ضعيفة ⚠️"
    
    # التوصية
    if is_auto:
        rec = "تجميع 🟢" if rsi < 40 else "احتفاظ ⚖️" if rsi < 70 else "جني أرباح ⚠️"
    else:
        rec = "إيجابي 🟢" if (close_prev and price > close_prev) else "سلبي 🔴"

    st.markdown(f"""
    <div class="report-card">
        <div style="text-align:center;">
            <span style="color:#3498db; font-size:13px;">💎 التقرير الفني لـ {symbol}</span><br>
            <b style="font-size:22px;">{name}</b>
        </div>
        <div class="separator"></div>
        <div class="info-line"><span>💰 السعر الحالي:</span> <b>{price:.3f} ج.م</b></div>
        <div class="info-line"><span>📢 التوصية:</span> <b>{rec}</b></div>
        
        <div class="separator"></div>
        <div class="info-line"><span>📊 قيمة السيولة:</span> <b>{vol:.2f} مليون ج.م</b></div>
        <div class="info-line"><span>💧 نبض السيولة:</span> <b>{liq_status}</b></div>
        
        <div class="separator"></div>
        <div class="label-blue">🔍 الأسباب الفنية:</div>
        <div class="info-line"><span>📟 مؤشر RSI:</span> <b>{rsi:.1f}</b></div>
        {f'<div class="info-line"><span>📈 فوق متوسط 50:</span> <b>{"نعم ✅" if price > ma50 else "لا ⚠️"}</b></div>' if ma50 else ''}
        
        <div class="separator"></div>
        <div class="label-blue">🚀 مستويات المقاومة (الأهداف):</div>
        <div class="info-line"><span>🔹 مقاومة 1: <b>{price*1.025:.3f}</b></span> <span>🔹 مقاومة 2: <b>{price*1.05:.3f}</b></span></div>
        
        <div class="label-blue">🛡️ مستويات الدعم:</div>
        <div class="info-line"><span>🔸 دعم 1: <b>{price*0.975:.3f}</b></span> <span>🔸 دعم 2: <b>{price*0.95:.3f}</b></span></div>
        
        <div class="separator"></div>
        <div class="label-blue">🏹 قسم المضارب والمستثمر:</div>
        <div class="info-line"><span>🚀 هدف مضاربي: <b>{price*1.03:.3f}</b></span> <span>🎯 هدف مستثمر: <b>{price*1.20:.3f}</b></span></div>
        {f'<div class="info-line"><span>🗓️ أعلى شهر: <b>{m_high:.3f}</b></span> <span>🔙 إغلاق أمس: <b>{close_prev:.3f}</b></span></div>' if close_prev else ''}
        
        <div class="separator"></div>
        <div style="color:#ff3b30; text-align:center; font-weight:bold; font-size:19px;">🛑 وقف الخسارة: {price*0.94:.3f}</div>
        <a href="https://wa.me/?text=تقرير {name}: {price:.3f}" class="wa-button">🚀 مشاركة التقرير</a>
    </div>
    """, unsafe_allow_html=True)

# 1. البحث الآلي
if u_input:
    try:
        data = yf.Ticker(f"{u_input}.CA").history(period="100d")
        if not data.empty:
            p = data['Close'].iloc[-1]
            v = (data['Volume'].iloc[-1] * p) / 1_000_000
            r = ta.rsi(data['Close']).iloc[-1]
            m = data['Close'].rolling(50).mean().iloc[-1]
            # هنا بنجيب الاسم من القاموس الجديد
            name = ARABIC_NAMES.get(u_input, "شركة متداولة")
            build_telegram_report(name, u_input, p, v, r, ma50=m)
    except: st.warning("تأكد من الرمز")

# 2. اللوحة اليدوية
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ الإدخال اليدوي</h3>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: p_m = st.number_input("💵 السعر الآن:", format="%.3f", key="p_m4")
with c2: h_m = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="h_m4")
with c3: l_m = st.number_input("📉 أقل اليوم:", format="%.3f", key="l_m4")
c4, c5, c6 = st.columns(3)
with c4: cl_m = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="cl_m4")
with c5: mh_m = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="mh_m4")
with c6: v_m = st.number_input("💧 السيولة (M):", format="%.2f", key="v_m4")

if p_m > 0:
    name_m = ARABIC_NAMES.get(u_input, "تحليل يدوي")
    build_telegram_report(name_m, u_input if u_input else "MANUAL", p_m, v_m, 50.0, close_prev=cl_m, m_high=mh_m, is_auto=False)
