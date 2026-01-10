import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS التنسيق الاحترافي ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d; margin: 15px auto;
    }
    .metric-box { background: #21262d; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #30363d; }
    .indicator-on { color: #238636; font-weight: bold; }
    .indicator-off { color: #da3633; font-weight: bold; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; padding: 15px; border-radius: 12px;
        text-align: center; font-weight: bold; display: block; text-decoration: none; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# قاعدة بيانات الأسماء (محدثة)
ARABIC_DB = {
    "SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم",
    "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري للمدفوعات",
    "BTFH": "بلتون المالية", "TMGH": "مجموعة طلعت مصطفى", "SWDY": "السويدي إليكتريك",
    "ATQA": "مصر الوطنية للصلب - عتاقة", "UNIT": "المتحدة للإسكان", "AMOC": "الإسكندرية للزيوت",
    "ORAS": "أوراسكوم كونستراكشون", "EKHO": "المصرية الكويتية", "PHDC": "بالم هيلز"
}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)

u_input = st.text_input("🔍 كود السهم (اختياري لو هتحلل يدوي):").upper().strip()

def build_card(name, sym, p, vol, rsi, sup, res, score, cl_p=0, m_h=0, high_d=0, low_d=0, is_auto=False, indicators=None):
    wa_msg = f"📊 تقرير {name} ({sym})\n💰 السعر: {p:.3f}\n⭐ التقييم: {score}/6\n🚀 المقاومة: {res:.2f}\n🛡️ الدعم: {sup:.2f}\n📊 السيولة: {vol:.1f}M"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    st.markdown(f"""
    <div class="report-card">
        <h2 style="text-align:center; margin-bottom:5px;">{name}</h2>
        <p style="text-align:center; color:#3498db; margin-top:0;">({sym})</p>
        
        <div style="display:flex; justify-content:space-around; margin:15px 0;">
            <div class="metric-box">💰 السعر<br><b>{p:.3f}</b></div>
            <div class="metric-box">⭐ التقييم<br><b>{score}/6</b></div>
            <div class="metric-box">📊 السيولة<br><b>{vol:.1f}M</b></div>
        </div>
    """, unsafe_allow_html=True)

    # إضافة فحص المؤشرات في حالة البحث الآلي فقط
    if is_auto and indicators:
        st.markdown(f"""
        <div style="background:#0d1117; padding:12px; border-radius:10px; border:1px dashed #30363d; margin-bottom:15px;">
            <p style="text-align:center; color:#3498db; font-weight:bold; margin-bottom:5px;">🔍 فحص المؤشرات الذكي (EMA, MACD, RSI):</p>
            <div style="display:flex; justify-content:space-between; font-size:13px;">
                <span>📈 فوق متوسط 50: <b class="{'indicator-on' if indicators['cond1'] else 'indicator-off'}">{'نعم ✅' if indicators['cond1'] else 'لا ⚠️'}</b></span>
                <span>💧 زخم الماكد: <b class="{'indicator-on' if indicators['cond2'] else 'indicator-off'}">{'إيجابي ✅' if indicators['cond2'] else 'سلبي ⚠️'}</b></span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
        <div style="margin-top:10px;">
            <p>🚀 <b>المقاومة الحالية:</b> <span style="color:#3498db; font-size:18px;">{res:.3f}</span></p>
            <p>🛡️ <b>الدعم الحالي:</b> <span style="color:#3498db; font-size:18px;">{sup:.3f}</span></p>
            <p style="text-align:center; color:#ff3b30; font-weight:bold; font-size:18px;">🛑 وقف الخسارة: {sup*0.98:.3f}</p>
        </div>
        
        <div style="background:#21262d; padding:10px; border-radius:8px; font-size:13px;">
            <div style="display:flex; justify-content:space-between;">
                <span>🔝 أعلى اليوم: <b>{high_d:.3f}</b></span>
                <span>📉 أقل اليوم: <b>{low_d:.3f}</b></span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:5px;">
                <span>🔙 إغلاق أمس: <b>{cl_p:.3f}</b></span>
                <span>🗓️ أعلى شهر: <b>{m_h:.3f}</b></span>
            </div>
        </div>
        
        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة التقرير الذكي عبر WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# --- التشغيل الآلي ---
if u_input:
    try:
        df = yf.Ticker(f"{u_input}.CA").history(period="1y")
        if not df.empty and len(df) > 50:
            df["EMA50"] = ta.ema(df["Close"], length=50)
            df["RSI"] = ta.rsi(df["Close"], length=14)
            macd_df = ta.macd(df["Close"])
            
            l = df.iloc[-1]
            p, r = l["Close"], l["RSI"]
            v = (l['Volume'] * p) / 1_000_000
            sup20, res20 = df["Low"].tail(20).min(), df["High"].tail(20).max()
            
            inds = {
                "cond1": p > l["EMA50"] if not pd.isna(l["EMA50"]) else False,
                "cond2": macd_df.iloc[-1]["MACD_12_26_9"] > macd_df.iloc[-1]["MACDs_12_26_9"],
                "cond3": r < 60,
                "cond4": p > df["Close"].iloc[-2]
            }
            sc = sum([inds["cond1"], inds["cond2"], inds["cond3"], inds["cond4"]]) + (2 if r < 35 else 0)
            
            build_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, v, r, sup20, res20, sc, 
                       cl_p=df["Close"].iloc[-2], m_h=df["High"].tail(22).max(), 
                       high_d=l["High"], low_d=l["Low"], is_auto=True, indicators=inds)
    except: st.error("عذراً، لم نجد بيانات لهذا السهم.")

# --- التحليل اليدوي (كل الخانات رجعت) ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color:white; text-align:center;'>🛠️ لوحة الإدخال اليدوي كاملة</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: p_m = st.number_input("💵 السعر الآن:", format="%.3f", key="p_m")
with c2: h_m = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="h_m")
with c3: l_m = st.number_input("📉 أقل اليوم:", format="%.3f", key="l_m")

c4, c5, c6 = st.columns(3)
with c4: cl_m = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="cl_m")
with c5: mh_m = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="mh_m")
with c6: v_m = st.number_input("💧 السيولة (M):", format="%.2f", key="v_m")

if p_m > 0:
    build_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", p_m, v_m, 50.0, p_m*0.97, p_m*1.03, 3, 
               cl_p=cl_m, m_h=mh_m, high_d=h_m, low_d=l_m, is_auto=False)
