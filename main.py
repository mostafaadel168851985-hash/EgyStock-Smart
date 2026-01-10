import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Sniper v47", layout="centered")

# --- CSS التنسيق الـ Modern Smart ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        margin: 15px auto; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .separator { border-top: 1px solid #333; margin: 15px 0; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 18px; margin-bottom: 5px; display: block; }
    .info-line { margin: 10px 0; font-size: 16px; display: flex; justify-content: space-between; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; padding: 15px; border-radius: 12px;
        text-align: center; font-weight: bold; display: block;
        text-decoration: none; margin-top: 25px;
        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- قاعدة بيانات شاملة مستخرجة من ملفك ---
ARABIC_NAMES = {
    "AALR": "العامة لاستصلاح الأراضي", "ABUK": "أبو قير للأسمدة", "ACAMD": "العربية لإدارة الأصول",
    "ACAP": "ايه كابيتال القابضة", "ACGC": "العربية لحليج الأقطان", "ADIB": "مصرف أبو ظبي الإسلامي",
    "AFDI": "الأهلي للتنمية والاستثمار", "ALCN": "الاسكندرية لتداول الحاويات", "AMOC": "الإسكندرية للزيوت المعدنية",
    "ANFI": "الإسكندرية للخدمات الطبية", "ARCC": "العربية للأسمنت", "ASCM": "أسيك للتعدين - أسكوم",
    "ATQA": "مصر الوطنية للصلب - عتاقة", "AUTO": "جي بي أوتو", "BINV": "بي انفستمنتس القابضة",
    "BTFH": "بلتون المالية القابضة", "COMI": "البنك التجاري الدولي", "DAPH": "المطورون العرب القابضة",
    "DICE": "دايس للملابس الجاهزة", "EAST": "الشرقية - ايسترن كومباني", "EKHO": "القابضة المصرية الكويتية",
    "ETEL": "المصرية للاتصالات", "FWRY": "فوري لتكنولوجيا البنوك", "HELI": "مصر الجديدة للإسكان",
    "JUFO": "جهينة للصناعات الغذائية", "MFOT": "مصر لإنتاج الأسمدة - موبكو", "MOED": "المصرية لنظم التعليم",
    "ORAS": "أوراسكوم كونستراكشون", "PHDC": "بالم هيلز للتعمير", "SWDY": "السويدي إليكتريك",
    "TMGH": "مجموعة طلعت مصطفى", "UEGC": "الصعيد العامة للمقاولات", "SCCD": "الصعيد العامة للمقاولات",
    "UNIP": "يونيفرسال لمواد التعبئة", "UNIT": "المتحدة للاسكان والتعمير", "UPMS": "الاتحاد الصيدلي للخدمات",
    "ALUM": "مصر للألومنيوم", "ESRS": "عز الدخيلة للصلب", "ISMA": "إسماعيلية مصر للدواجن",
    "RAYA": "راية القابضة للاستثمارات", "RACC": "راية لخدمات مراكز الاتصال", "CLHO": "كليوباترا للمستشفيات",
    "CCAP": "القلعة للاستشارات", "ORWE": "النساجون الشرقيون", "SKPC": "سيدي كرير للبتروكيماويات",
    "AMER": "عامر جروب القابضة", "MNHD": "مدينة مصر للاسكان", "ADRE": "العقارية للبنوك الوطنية",
    "ODIN": "أودن للاستثمارات المالية", "COPR": "النصر للملابس والمنسوجات - كابو", "CSAG": "القاهرة للصناعات الغذائية - كوكي"
}

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً ARCC, ALUM, SCCD):").upper().strip()

def build_modern_card(name, symbol, price, vol, rsi, ma50=None, cl_p=0, m_h=0, is_auto=True):
    liq_status = "طبيعية ⚖️" if vol > 10 else "ضعيفة ⚠️"
    rec = "تجميع 🟢" if rsi < 40 else "احتفاظ ⚖️" if rsi < 70 else "جني أرباح ⚠️"
    
    # حساب الأهداف والدعوم
    res1, res2 = price*1.025, price*1.05
    sup1, sup2 = price*0.975, price*0.95

    # تجهيز رسالة واتساب كاملة
    wa_msg = (f"🎯 تقرير سهم: {name}\n"
              f"💰 السعر الحالي: {price:.3f}\n"
              f"📢 التوصية: {rec}\n"
              f"🚀 الأهداف: {res1:.3f} | {res2:.3f}\n"
              f"🛡️ الدعوم: {sup1:.3f} | {sup2:.3f}\n"
              f"📊 السيولة: {vol:.2f} M")
    
    import urllib.parse
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    st.markdown(f"""
    <div class="report-card">
        <div style="text-align:center;">
            <span style="color:#3498db; font-size:14px; letter-spacing:1px;">REPORT: {symbol}</span><br>
            <b style="font-size:24px;">{name}</b>
        </div>
        <div class="separator"></div>
        <div class="info-line"><span>💰 السعر الحالي:</span> <b>{price:.3f} ج.م</b></div>
        <div class="info-line"><span>📢 التوصية:</span> <b>{rec}</b></div>
        <div class="separator"></div>
        <div class="info-line"><span>📊 قيمة السيولة:</span> <b>{vol:.2f} مليون</b></div>
        <div class="info-line"><span>💧 نبض السيولة:</span> <b>{liq_status}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🔍 الأسباب الفنية:</div>
        <div class="info-line"><span>📟 مؤشر RSI:</span> <b>{rsi:.1f}</b></div>
        <div class="info-line"><span>📈 فوق متوسط 50:</span> <b>{'نعم ✅' if (ma50 and price > ma50) else 'لا ⚠️'}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🚀 الأهداف والمقاومات:</div>
        <div class="info-line"><span>🔹 هدف 1: <b>{res1:.3f}</b></span> <span>🔹 هدف 2: <b>{res2:.3f}</b></span></div>
        <div class="label-blue">🛡️ مستويات الدعم:</div>
        <div class="info-line"><span>🔸 دعم 1: <b>{sup1:.3f}</b></span> <span>🔸 دعم 2: <b>{sup2:.3f}</b></span></div>
        <div class="separator"></div>
        <div class="label-blue">🏹 قسم المستثمر والمضارب:</div>
        <div class="info-line"><span>🚀 هدف سريع: <b>{price*1.03:.3f}</b></span> <span>🎯 هدف بعيد: <b>{price*1.20:.3f}</b></span></div>
        <div class="info-line"><span>🗓️ أعلى شهر: <b>{m_h:.3f}</b></span> <span>🔙 إغلاق أمس: <b>{cl_p:.3f}</b></span></div>
        <div class="separator"></div>
        <div style="color:#ff3b30; text-align:center; font-weight:bold; font-size:19px;">🛑 وقف الخسارة: {price*0.94:.3f}</div>
        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة التقرير الكامل عبر WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# 1. الآلي
if u_input:
    try:
        data = yf.Ticker(f"{u_input}.CA").history(period="100d")
        if not data.empty:
            p = data['Close'].iloc[-1]
            v = (data['Volume'].iloc[-1] * p) / 1_000_000
            r = ta.rsi(data['Close']).iloc[-1]
            m = data['Close'].rolling(50).mean().iloc[-1]
            build_modern_card(ARABIC_NAMES.get(u_input, "شركة متداولة"), u_input, p, v, r, ma50=m)
    except: pass

# 2. اليدوي الكامل (6 خانات)
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ الإدخال اليدوي الكامل</h3>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: p_m = st.number_input("💵 السعر الآن:", format="%.3f", key="p47")
with c2: h_m = st.number_input("🔝 أعلى سعر:", format="%.3f", key="h47")
with c3: l_m = st.number_input("📉 أقل سعر:", format="%.3f", key="l47")
c4, c5, c6 = st.columns(3)
with c4: cl_m = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="c47")
with c5: mh_m = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="mh47")
with c6: v_m = st.number_input("💧 السيولة (M):", format="%.2f", key="v47")

if p_m > 0:
    name_m = ARABIC_NAMES.get(u_input, "تحليل يدوي")
    build_modern_card(name_m, u_input if u_input else "MANUAL", p_m, v_m, 50.0, cl_p=cl_m, m_h=mh_m, is_auto=False)
