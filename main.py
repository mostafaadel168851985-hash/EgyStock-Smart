import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Sniper v43", layout="centered")

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
    .label-blue { color: #3498db; font-weight: bold; font-size: 18px; margin-bottom: 5px; display: block; }
    .info-line { margin: 10px 0; font-size: 16px; display: flex; justify-content: space-between; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 12px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- القاموس الكامل (بما فيهم ARCC و ALUM) ---
ARABIC_NAMES = {
    "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم", "AALR": "العامة لاستصلاح الأراضي",
    "ABUK": "أبو قير للأسمدة", "ACAMD": "العربية لإدارة الأصول", "ACAP": "ايه كابيتال القابضة",
    "ACGC": "العربية لحليج الأقطان", "ADIB": "مصرف أبو ظبي الإسلامي", "AFDI": "الأهلي للتنمية والاستثمار",
    "ALCN": "الاسكندرية لتداول الحاويات", "AMOC": "الإسكندرية للزيوت المعدنية", "ATQA": "مصر الوطنية للصلب - عتاقة",
    "BTFH": "بلتون المالية القابضة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري للمدفوعات",
    "SWDY": "السويدي إليكتريك", "TMGH": "مجموعة طلعت مصطفى", "UEGC": "الصعيد العامة للمقاولات",
    "SCCD": "الصعيد العامة للمقاولات", "UNIP": "يونيفرسال لمواد التعبئة", "UNIT": "المتحدة للاسكان",
    "MFOT": "موبكو للأسمدة", "HELI": "مصر الجديدة للاسكان"
}

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً ARCC أو ALUM):").upper().strip()

def build_card(name, symbol, price, vol, rsi, ma50=None, close_prev=None, m_high=None, is_auto=True):
    liq_status = "طبيعية ⚖️" if vol > 10 else "ضعيفة ⚠️"
    
    # منطق التوصية الذكية (سعر + سيولة)
    if is_auto:
        rec = "تجميع 🟢" if rsi < 40 else "احتفاظ ⚖️" if rsi < 70 else "جني أرباح ⚠️"
    else:
        if price > close_prev:
            rec = "شراء قوي 🟢" if vol > 10 else "صعود حذر ⚠️"
        else:
            rec = "تخارج / سلبي 🔴" if vol > 15 else "هدوء / مراقبة ⚖️"

    # عرض الكارت
    st.markdown(f"""
    <div class="report-card">
        <div style="text-align:center;">
            <span style="color:#3498db; font-size:13px;">💎 التقرير الفني لـ {symbol}</span><br>
            <b style="font-size:24px;">{name}</b>
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
        <div class="info-line"><span>📈 فوق متوسط 50:</span> <b>{'نعم ✅' if (ma50 and price > ma50) else 'لا ⚠️'}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🚀 مستويات المقاومة (الأهداف):</div>
        <div class="info-line"><span>🔹 مقاومة 1: <b>{price*1.025:.3f}</b></span> <span>🔹 مقاومة 2: <b>{price*1.05:.3f}</b></span></div>
        <div class="label-blue">🛡️ مستويات الدعم:</div>
        <div class="info-line"><span>🔸 دعم 1: <b>{price*0.975:.3f}</b></span> <span>🔸 دعم 2: <b>{price*0.95:.3f}</b></span></div>
        <div class="separator"></div>
        <div class="label-blue">🏹 قسم المضارب والمستثمر:</div>
        <div class="info-line"><span>🚀 هدف مضاربي: <b>{price*1.03:.3f}</b></span> <span>🎯 هدف مستثمر: <b>{price*1.20:.3f}</b></span></div>
        {f'<div class="info-line"><span>🗓️ أعلى شهر: <b>{m_high:.3f}</b></span> <span>🔙 إغلاق أمس: <b>{close_prev:.3f}</b></span></div>' if not is_auto else ''}
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
            name = ARABIC_NAMES.get(u_input, "شركة متداولة")
            build_card(name, u_input, p, v, r, ma50=m)
    except: pass

# 2. اللوحة اليدوية الكاملة (الـ 6 خانات)
st.markdown("<hr style='border-color:#444;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة الإدخال اليدوي الكاملة</h3>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: p_m = st.number_input("💵 السعر الآن:", format="%.3f", key="pm43")
with c2: h_m = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="hm43")
with c3: l_m = st.number_input("📉 أقل اليوم:", format="%.3f", key="lm43")
c4, c5, c6 = st.columns(3)
with c4: cl_m = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="cm43")
with c5: mh_m = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="mhm43")
with c6: v_m = st.number_input("💧 السيولة (M):", format="%.2f", key="vm43")

if p_m > 0:
    name_m = ARABIC_NAMES.get(u_input, "تحليل يدوي")
    build_card(name_m, u_input if u_input else "MANUAL", p_m, v_m, 50.0, close_prev=cl_m, m_high=mh_m, is_auto=False)
