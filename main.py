import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.parse

st.set_page_config(page_title="EGX Sniper v51", layout="centered")

# --- CSS التنسيق المودرن ---
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

# --- قاعدة بيانات الأسماء المستخرجة من ملفك بالكامل ---
FULL_DB = {
    "AALR": "العامة لاستصلاح الأراضي", "ABUK": "أبو قير للأسمدة", "ACAMD": "العربية لإدارة وتطوير الأصول",
    "ACAP": "ايه كابيتال القابضة", "ACGC": "العربية لحليج الأقطان", "ADIB": "مصرف أبو ظبي الإسلامي",
    "AFDI": "الأهلي للتنمية والاستثمار", "ALCN": "الاسكندرية لتداول الحاويات", "AMOC": "الإسكندرية للزيوت المعدنية",
    "ANFI": "الإسكندرية للخدمات الطبية", "ARCC": "العربية للأسمنت", "ASCM": "أسيك للتعدين - أسكوم",
    "ATQA": "مصر الوطنية للصلب - عتاقة", "AUTO": "جي بي أوتو", "BINV": "بي انفستمنتس القابضة",
    "BTFH": "بلتون المالية القابضة", "CANA": "قناة السويس لتكنولوجيا المعلومات", "CCAP": "القلعة للاستشارات",
    "CIEB": "بنك كريدي أجريكول", "CLHO": "كليوباترا للمستشفيات", "COMI": "البنك التجاري الدولي",
    "CONV": "كونتكت المالية القابضة", "DAPH": "المطورون العرب القابضة", "DICE": "دايس للملابس الجاهزة",
    "EAST": "الشرقية - ايسترن كومباني", "EDBM": "المصريين في الخارج للاستثمار", "EFIC": "المالية والصناعية المصرية",
    "EFID": "إيديتا للصناعات الغذائية", "EGAL": "مصر للألومنيوم", "EGCH": "الكيماويات المصرية - كيما",
    "EGTS": "المصرية للمنتجعات", "EKHO": "القابضة المصرية الكويتية", "ELSH": "الشمس للإسكان والتعمير",
    "EMFD": "إعمار مصر للتنمية", "ESRS": "عز الدخيلة للصلب", "ETEL": "المصرية للاتصالات",
    "FWRY": "فوري للمدفوعات", "GBOR": "جي بي أوتو", "HELI": "مصر الجديدة للإسكان",
    "ISMA": "إسماعيلية مصر للدواجن", "JUFO": "جهينة للصناعات الغذائية", "KABO": "النصر للملابس - كابو",
    "MFOT": "مصر لإنتاج الأسمدة - موبكو", "MICH": "مصر لصناعة الكيماويات", "MNHD": "مدينة مصر للإسكان",
    "MPCO": "المنصورة للدواجن", "ORAS": "أوراسكوم كونستراكشون", "ORWE": "النساجون الشرقيون",
    "PHDC": "بالم هيلز للتعمير", "RAYA": "راية القابضة", "RMDA": "راميدا للأدوية",
    "SKPC": "سيدي كرير للبتروكيماويات", "SVCE": "جنوب الوادي للأسمنت", "SWDY": "السويدي إليكتريك",
    "TMGH": "طلعت مصطفى", "UEGC": "الصعيد العامة للمقاولات", "SCCD": "الصعيد العامة للمقاولات",
    "UNIP": "يونيفرسال لمواد التعبئة", "UNIT": "المتحدة للإسكان", "UPMS": "الاتحاد الصيدلي", "ALUM": "مصر للألومنيوم"
}

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً SVCE أو ARCC):").upper().strip()

def build_card(name, symbol, price, vol, rsi, ma50=None, cl_p=0, m_h=0, is_auto=True):
    res1, res2 = price * 1.025, price * 1.05
    sup1, sup2 = price * 0.975, price * 0.95
    liq_status = "طبيعية ⚖️" if vol > 10 else "ضعيفة ⚠️"
    rec = "تجميع 🟢" if rsi < 40 else "احتفاظ ⚖️" if rsi < 70 else "جني أرباح ⚠️"
    
    # رسالة الواتساب الاحترافية بنجوم وتنسيق ثندر
    wa_text = (f"🎯 *تقرير سهم: {name} ({symbol})*\n"
               f"💰 *السعر الحالي:* {price:.3f} ج.م\n"
               f"📢 *التوصية:* {rec}\n\n"
               f"🚀 *المقاومات:* {res1:.2f} | {res2:.2f}\n"
               f"🛡️ *الدعوم:* {sup1:.2f} | {sup2:.2f}\n"
               f"📊 *السيولة:* {vol:.2f} مليون ج.م\n"
               f"📟 *مؤشر RSI:* {rsi:.1f}\n\n"
               f"🛑 *وقف الخسارة:* {price*0.94:.2f}")
    
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_text)}"

    st.markdown(f"""
    <div class="report-card">
        <div style="text-align:center;">
            <b style="font-size:24px;">{name}</b><br>
            <span style="color:#3498db;">({symbol})</span>
        </div>
        <div class="separator"></div>
        <div class="info-line"><span>💰 السعر الحالي:</span> <b>{price:.3f}</b></div>
        <div class="info-line"><span>📢 التوصية:</span> <b>{rec}</b></div>
        <div class="separator"></div>
        <div class="info-line"><span>📊 السيولة:</span> <b>{vol:.2f} M</b></div>
        <div class="info-line"><span>💧 نبض السيولة:</span> <b>{liq_status}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🚀 الأهداف:</div>
        <div class="info-line"><span>🔹 مقاومة 1: {res1:.3f}</span> <span>🔹 مقاومة 2: {res2:.3f}</span></div>
        <div class="label-blue">🛡️ الدعوم:</div>
        <div class="info-line"><span>🔸 دعم 1: {sup1:.3f}</span> <span>🔸 دعم 2: {sup2:.3f}</span></div>
        <div class="separator"></div>
        <div class="info-line"><span>📟 RSI: <b>{rsi:.1f}</b></span> <span>🔙 إغلاق: <b>{cl_p:.3f}</b></span></div>
        <div style="color:#ff3b30; text-align:center; font-weight:bold; font-size:19px; margin-top:10px;">🛑 وقف الخسارة: {price*0.94:.3f}</div>
        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة التقرير عبر WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# البحث الآلي
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

# الإدخال اليدوي (6 خانات)
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color:white; text-align:center;'>🛠️ لوحة الإدخال اليدوي</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: p_m = st.number_input("السعر:", format="%.3f", key="p51")
with c2: h_m = st.number_input("أعلى:", format="%.3f", key="h51")
with c3: l_m = st.number_input("أقل:", format="%.3f", key="l51")
c4, c5, c6 = st.columns(3)
with c4: cl_m = st.number_input("إغلاق أمس:", format="%.3f", key="c51")
with c5: mh_m = st.number_input("أعلى شهر:", format="%.3f", key="mh51")
with c6: v_m = st.number_input("سيولة:", format="%.2f", key="v51")

if p_m > 0:
    build_card(FULL_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", p_m, v_m, 50.0, cl_p=cl_m, m_h=mh_m, is_auto=False)
