import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Sniper v45", layout="centered")

# --- CSS التنسيق النهائي ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        margin: 15px auto;
    }
    .separator { border-top: 1px solid #444; margin: 15px 0; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 18px; display: block; }
    .info-line { margin: 10px 0; font-size: 16px; display: flex; justify-content: space-between; }
    .wa-link {
        background-color: #25d366; color: white !important; padding: 15px; 
        border-radius: 10px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- القاموس الكامل (تأكد من وجود ARCC و ALUM) ---
ARABIC_NAMES = {
    "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "AALR": "العامة لاستصلاح الأراضي",
    "ABUK": "أبو قير للأسمدة", "ACAMD": "العربية لإدارة الأصول", "ACAP": "ايه كابيتال القابضة",
    "ACGC": "العربية لحليج الأقطان", "ADIB": "مصرف أبو ظبي الإسلامي", "AFDI": "الأهلي للتنمية والاستثمار",
    "ALCN": "الاسكندرية لتداول الحاويات", "AMOC": "الإسكندرية للزيوت المعدنية", "ATQA": "مصر الوطنية للصلب - عتاقة",
    "BTFH": "بلتون المالية القابضة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري للمدفوعات",
    "SWDY": "السويدي إليكتريك", "TMGH": "مجموعة طلعت مصطفى", "UEGC": "الصعيد العامة للمقاولات",
    "SCCD": "الصعيد العامة للمقاولات", "UNIP": "يونيفرسال لمواد التعبئة", "UNIT": "المتحدة للاسكان",
    "MFOT": "موبكو للأسمدة", "HELI": "مصر الجديدة للاسكان", "EKHO": "القابضة المصرية الكويتية"
}

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً ARCC أو ALUM):").upper().strip()

def build_card(name, symbol, price, vol, rsi, ma50=None, cl_prev=0, m_high=0, is_auto=True):
    liq_status = "طبيعية ⚖️" if vol > 10 else "ضعيفة ⚠️"
    rec = "تجميع 🟢" if rsi < 40 else "احتفاظ ⚖️" if rsi < 70 else "جني أرباح ⚠️"
    
    if not is_auto:
        rec = "إيجابي 🟢" if price > cl_prev else "سلبي 🔴"

    # تجهيز رابط الواتساب
    wa_msg = f"تقرير {name}: السعر {price:.3f}"
    wa_url = f"https://wa.me/?text={wa_msg}"

    card_html = f"""
    <div class="report-card">
        <div style="text-align:center;">
            <span style="color:#3498db;">💎 التقرير الفني لـ {symbol}</span><br>
            <b style="font-size:22px;">{name}</b>
        </div>
        <div class="separator"></div>
        <div class="info-line"><span>💰 السعر الحالي:</span> <b>{price:.3f}</b></div>
        <div class="info-line"><span>📢 التوصية:</span> <b>{rec}</b></div>
        <div class="separator"></div>
        <div class="info-line"><span>📊 قيمة السيولة:</span> <b>{vol:.2f} M</b></div>
        <div class="info-line"><span>💧 نبض السيولة:</span> <b>{liq_status}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🔍 الأسباب الفنية:</div>
        <div class="info-line"><span>📟 مؤشر RSI:</span> <b>{rsi:.1f}</b></div>
        <div class="info-line"><span>📈 فوق متوسط 50:</span> <b>{'نعم ✅' if (ma50 and price > ma50) else 'لا ⚠️'}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🚀 الأهداف:</div>
        <div class="info-line"><span>🔹 مقاومة 1: {price*1.025:.3f}</span> <span>🔹 مقاومة 2: {price*1.05:.3f}</span></div>
        <div class="label-blue">🛡️ الدعوم:</div>
        <div class="info-line"><span>🔸 دعم 1: {price*0.975:.3f}</span> <span>🔸 دعم 2: {price*0.95:.3f}</span></div>
        <div class="separator"></div>
        <div class="label-blue">🏹 قسم المضارب والمستثمر:</div>
        <div class="info-line"><span>🚀 هدف مضاربي: {price*1.03:.3f}</span> <span>🎯 هدف مستثمر: {price*1.20:.3f}</span></div>
        <div class="info-line"><span>🗓️ أعلى شهر: {m_high:.3f}</span> <span>🔙 إغلاق أمس: {cl_prev:.3f}</span></div>
        <div class="separator"></div>
        <div style="color:#ff3b30; text-align:center; font-weight:bold; font-size:18px;">🛑 وقف الخسارة: {price*0.94:.3f}</div>
        <a href="{wa_url}" target="_blank" class="wa-link">🚀 مشاركة عبر واتساب</a>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# 1. الآلي
if u_input:
    try:
        df = yf.Ticker(f"{u_input}.CA").history(period="100d")
        if not df.empty:
            p = df['Close'].iloc[-1]
            v = (df['Volume'].iloc[-1] * p) / 1_000_000
            r = ta.rsi(df['Close']).iloc[-1]
            m = df['Close'].rolling(50).mean().iloc[-1]
            build_card(ARABIC_NAMES.get(u_input, "شركة متداولة"), u_input, p, v, r, ma50=m)
    except: pass

# 2. اليدوي (6 خانات)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ الإدخال اليدوي</h3>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: p_m = st.number_input("السعر:", format="%.3f", key="p")
with c2: h_m = st.number_input("أعلى:", format="%.3f", key="h")
with c3: l_m = st.number_input("أقل:", format="%.3f", key="l")
c4, c5, c6 = st.columns(3)
with c4: cl_m = st.number_input("إغلاق أمس:", format="%.3f", key="cl")
with c5: mh_m = st.number_input("أعلى شهر:", format="%.3f", key="mh")
with c6: v_m = st.number_input("سيولة (M):", format="%.2f", key="v")

if p_m > 0:
    build_card(ARABIC_NAMES.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", p_m, v_m, 50.0, cl_prev=cl_m, m_high=mh_m, is_auto=False)
