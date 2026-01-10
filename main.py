import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.parse

st.set_page_config(page_title="EGX Sniper Smart Pro", layout="centered")

# --- التنسيق البصري الاحترافي ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        margin: 15px auto; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .label-blue { color: #3498db; font-weight: bold; font-size: 18px; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; padding: 15px; border-radius: 12px;
        text-align: center; font-weight: bold; display: block;
        text-decoration: none; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# قاعدة بيانات الأسماء (مستخرجة من الشيت والرموز المشهورة)
ARABIC_DB = {
    "SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم",
    "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري للمدفوعات",
    "BTFH": "بلتون المالية القابضة", "TMGH": "مجموعة طلعت مصطفى", "SWDY": "السويدي إليكتريك",
    "ATQA": "مصر الوطنية للصلب - عتاقة", "UNIT": "المتحدة للإسكان", "AMOC": "الإسكندرية للزيوت",
    "EGTS": "المصرية للمنتجعات", "RMDA": "راميدا للأدوية", "CIEB": "بنك كريدي أجريكول"
}

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص: التحليل الذكي</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل كود السهم (مثلاً SVCE):").upper().strip()

@st.cache_data(ttl=900) # كاش لمدة 15 دقيقة للسرعة
def get_smart_data(symbol):
    try:
        df = yf.Ticker(f"{symbol}.CA").history(period="1y")
        return df
    except: return pd.DataFrame()

def build_smart_card(name, symbol, price, vol, rsi, sup, res, score, cl_p=0):
    # تحديد الحالة بناءً على التحليل الذكي (Score)
    if score >= 5: 
        status = "إشارة قوية جداً 🟢"
        advice = "السهم في منطقة قوة فنية"
    elif score >= 3: 
        status = "مراقبة / احتفاظ ⚖️"
        advice = "حركة عرضية تميل للإيجابية"
    else: 
        status = "إشارة ضعيفة 🔴"
        advice = "يفضل الانتظار أو تخفيف المراكز"

    # رسالة الواتساب الاحترافية بالتحليل الجديد
    wa_msg = (f"🎯 *تقرير ذكي: {name} ({symbol})*\n"
              f"💰 *السعر:* {price:.3f}\n"
              f"⭐ *التقييم:* {score}/6 ({status})\n\n"
              f"🚀 *المقاومة:* {res:.2f}\n"
              f"🛡️ *الدعم:* {sup:.2f}\n"
              f"📊 *السيولة:* {vol:.2f} M\n"
              f"🛑 *وقف الخسارة:* {sup*0.98:.2f}")
    
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    st.markdown(f"""
    <div class="report-card">
        <div style="text-align:center;">
            <b style="font-size:26px;">{name}</b><br>
            <span style="color:#3498db;">({symbol})</span>
        </div>
        <div class="separator"></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span>💰 السعر: <b>{price:.3f}</b></span>
            <span>⭐ التقييم: <b>{score}/6</b></span>
        </div>
        <div style="text-align:center; background:#2c3e50; padding:10px; border-radius:8px; margin-bottom:15px;">
            <b>الحالة: {status}</b><br><small>{advice}</small>
        </div>
        <div class="label-blue">🚀 الأهداف الذكية (المقاومات):</div>
        <p>مقاومة قريبة: <b>{res:.3f}</b> | هدف (5%): <b>{price*1.05:.3f}</b></p>
        <div class="label-blue">🛡️ مستويات الأمان (الدعوم):</div>
        <p>دعم رئيسي: <b>{sup:.3f}</b> | إغلاق أمس: <b>{cl_p:.3f}</b></p>
        <div class="separator"></div>
        <div style="display:flex; justify-content:space-between; font-size:14px;">
            <span>📊 سيولة: {vol:.2f}M</span>
            <span>📟 RSI: {rsi:.1f}</span>
            <span>📉 وقف: {sup*0.98:.2f}</span>
        </div>
        <a href="{wa_url}" target="_blank" class="wa-button">📲 إرسال التحليل الذكي عبر WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

if u_input:
    df = get_smart_data(u_input)
    if not df.empty:
        # حساب المؤشرات الفنية للتحليل الذكي
        df["EMA50"] = ta.ema(df["Close"], length=50)
        df["RSI"] = ta.rsi(df["Close"], length=14)
        macd = ta.macd(df["Close"])
        df = pd.concat([df, macd], axis=1)
        
        last = df.iloc[-1]
        p, r = last["Close"], last["RSI"]
        vol_m = (last['Volume'] * p) / 1_000_000
        
        # استخراج الدعم والمقاومة من حركة السعر الحقيقية
        sup_20 = df["Low"].tail(20).min()
        res_20 = df["High"].tail(20).max()
        
        # حساب السكور (التحليل الذكي)
        sc = 0
        if p > last["EMA50"]: sc += 1
        if r < 45: sc += 2 # تشبع بيعي (إيجابي)
        elif r < 65: sc += 1 # منطقة أمان
        if last["MACD_12_26_9"] > last["MACDs_12_26_9"]: sc += 2 # تقاطع إيجابي
        if p > df["Close"].iloc[-2]: sc += 1 # زخم صاعد
        
        build_smart_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, vol_m, r, sup_20, res_20, sc, cl_p=df["Close"].iloc[-2])

# اللوحة اليدوية
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color:white; text-align:center;'>🛠️ إدخال يدوي</h4>", unsafe_allow_html=True)
c1, v1 = st.columns(2)
with c1: p_manual = st.number_input("السعر الحالي:", format="%.3f")
with v1: v_manual = st.number_input("السيولة (M):", format="%.2f")

if p_manual > 0:
    build_smart_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", p_manual, v_manual, 50.0, p_manual*0.97, p_manual*1.03, 3)
