import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.parse

st.set_page_config(page_title="EGX Sniper v50", layout="centered")

# --- CSS التنسيق (المودرن اللي عجبك) ---
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

# --- قاعدة البيانات (تم إضافة جنوب الوادي SVCE وأسهم ثندر) ---
FULL_DB = {
    "SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم",
    "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري للمدفوعات",
    "BTFH": "بلتون المالية القابضة", "TMGH": "مجموعة طلعت مصطفى", "SWDY": "السويدي إليكتريك",
    "UEGC": "الصعيد العامة للمقاولات", "SCCD": "الصعيد العامة للمقاولات", "UNIT": "المتحدة للاسكان",
    "AMOC": "الإسكندرية للزيوت المعدنية", "ALCN": "الاسكندرية لتداول الحاويات", "EKHO": "المصرية الكويتية",
    "PHDC": "بالم هيلز للتعمير", "CCAP": "القلعة للاستشارات", "MFOT": "موبكو للأسمدة"
}

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً SVCE أو ARCC):").upper().strip()

def build_card(name, symbol, price, vol, rsi, ma50=None, cl_p=0, m_h=0, is_auto=True):
    # 1. حساب الدعم والمقاومة (أوتوماتيك)
    res1, res2 = price * 1.025, price * 1.05
    sup1, sup2 = price * 0.975, price * 0.95
    
    # 2. التوصية ونبض السيولة
    liq_status = "طبيعية ⚖️" if vol > 10 else "ضعيفة ⚠️"
    rec = "تجميع 🟢" if rsi < 40 else "احتفاظ ⚖️" if rsi < 70 else "جني أرباح ⚠️"
    if not is_auto and cl_p > 0:
        rec = "إيجابي 🟢" if price > cl_p else "سلبي 🔴"

    # 3. تجهيز رسالة الواتساب "كاملة" بكل المعلومات
    wa_text = (f"🎯 *تقرير سهم: {name} ({symbol})*\n"
               f"💰 *السعر الحالي:* {price:.3f} ج.م\n"
               f"📢 *التوصية:* {rec}\n\n"
               f"🚀 *المقاومات:* {res1:.2f} | {res2:.2f}\n"
               f"🛡️ *الدعوم:* {sup1:.2f} | {sup2:.2f}\n"
               f"📊 *السيولة:* {vol:.2f} مليون ج.م\n\n"
               f"🛑 *وقف الخسارة:* {price*0.94:.2f}")
    
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_text)}"

    # 4. عرض الكارت على الشاشة
    st.markdown(f"""
    <div class="report-card">
        <div style="text-align:center;">
            <span style="color:#3498db; font-size:14px;">REPORT: {symbol}</span><br>
            <b style="font-size:24px;">{name}</b>
        </div>
        <div class="separator"></div>
        <div class="info-line"><span>💰 السعر الحالي:</span> <b>{price:.3f} ج.م</b></div>
        <div class="info-line"><span>📢 التوصية:</span> <b>{rec}</b></div>
        <div class="separator"></div>
        <div class="info-line"><span>📊 قيمة السيولة:</span> <b>{vol:.2f} مليون</b></div>
        <div class="info-line"><span>💧 نبض السيولة:</span> <b>{liq_status}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🚀 مستويات المقاومة (الأهداف):</div>
        <div class="info-line"><span>🔹 مقاومة 1: <b>{res1:.3f}</b></span> <span>🔹 مقاومة 2: <b>{res2:.3f}</b></span></div>
        <div class="label-blue">🛡️ مستويات الدعم:</div>
        <div class="info-line"><span>🔸 دعم 1: <b>{sup1:.3f}</b></span> <span>🔸 دعم 2: <b>{sup2:.3f}</b></span></div>
        <div class="separator"></div>
        <div class="label-blue">📈 مؤشرات فنية:</div>
        <div class="info-line"><span>📟 مؤشر RSI:</span> <b>{rsi:.1f}</b></div>
        <div class="info-line"><span>🗓️ أعلى شهر: <b>{m_h:.3f}</b></span> <span>🔙 إغلاق أمس: <b>{cl_p:.3f}</b></span></div>
        <div class="separator"></div>
        <div style="color:#ff3b30; text-align:center; font-weight:bold; font-size:19px;">🛑 وقف الخسارة: {price*0.94:.3f}</div>
        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة التقرير الكامل عبر WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# --- الجزء الآلي ---
if u_input:
    try:
        data = yf.Ticker(f"{u_input}.CA").history(period="100d")
        if not data.empty:
            p = data['Close'].iloc[-1]
            v = (data['Volume'].iloc[-1] * p) / 1_000_000
            r = ta.rsi(data['Close']).iloc[-1]
            m = data['Close'].rolling(50).mean().iloc[-1]
            build_card(FULL_DB.get(u_input, "شركة متداولة"), u_input, p, v, r, ma50=m)
    except: pass

# --- الجزء اليدوي (6 خانات) ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة الإدخال اليدوي</h3>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: p_m = st.number_input("💵 السعر الآن:", format="%.3f", key="p50")
with c2: h_m = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="h50")
with c3: l_m = st.number_input("📉 أقل اليوم:", format="%.3f", key="l50")
c4, c5, c6 = st.columns(3)
with c4: cl_m = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="c50")
with c5: mh_m = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="mh50")
with c6: v_m = st.number_input("💧 السيولة (M):", format="%.2f", key="v50")

if p_m > 0:
    build_card(FULL_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", p_m, v_m, 50.0, cl_p=cl_m, m_h=mh_m, is_auto=False)
