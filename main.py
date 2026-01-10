import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.parse

st.set_page_config(page_title="EGX Smart Analyzer v57", layout="centered")

# --- CSS التنسيق (إضافة ألوان المؤشرات) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d; margin: 15px auto;
    }
    .metric-box {
        background: #21262d; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #30363d;
    }
    .indicator-on { color: #238636; font-weight: bold; } /* أخضر للمؤشرات الإيجابية */
    .indicator-off { color: #da3633; font-weight: bold; } /* أحمر للسلبية */
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; padding: 15px; border-radius: 12px;
        text-align: center; font-weight: bold; display: block; text-decoration: none; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- قاعدة البيانات الشاملة من ملفك ---
ARABIC_DB = {
    "SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم",
    "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري",
    "BTFH": "بلتون المالية", "TMGH": "طلعت مصطفى", "SWDY": "السويدي إليكتريك",
    "ATQA": "عتاقة للصلب", "UNIT": "المتحدة للإسكان", "AMOC": "إسكندرية للزيوت",
    "EGTS": "المصرية للمنتجعات", "RMDA": "راميدا", "CIEB": "كريدي أجريكول",
    "ACAMD": "العربية لإدارة الأصول", "ACGC": "العربية لحليج الأقطان", "AFDI": "الأهلي للتنمية"
}

st.markdown("<h1 style='text-align:center; color:white;'>🚀 رادار التحليل الذكي v57</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل كود السهم (مثلاً SVCE):").upper().strip()

@st.cache_data(ttl=600)
def load_smart_data(symbol):
    try:
        df = yf.Ticker(f"{symbol}.CA").history(period="1y")
        if df.empty: return pd.DataFrame()
        df["EMA50"] = ta.ema(df["Close"], length=50)
        df["EMA200"] = ta.ema(df["Close"], length=200)
        df["RSI"] = ta.rsi(df["Close"], length=14)
        macd = ta.macd(df["Close"])
        df = pd.concat([df, macd], axis=1)
        return df
    except: return pd.DataFrame()

def build_visual_card(name, sym, df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    p = last["Close"]
    rsi = last["RSI"]
    vol = (last['Volume'] * p) / 1_000_000
    
    # 1. تحليل المؤشرات (الذكاء المكشوف)
    cond1 = p > last["EMA50"]      # السعر فوق المتوسط
    cond2 = last["MACD_12_26_9"] > last["MACDs_12_26_9"] # تقاطع الماكد
    cond3 = rsi < 60               # السهم مش متشبع شراء
    cond4 = p > prev["Close"]      # صعود سعري
    
    # حساب السكور
    score = sum([cond1, cond2, cond3, cond4]) + (2 if rsi < 35 else 0)
    
    # تحديد الدعم والمقاومة الحقيقيين
    sup = df["Low"].tail(20).min()
    res = df["High"].tail(20).max()

    # رسالة الواتساب
    wa_msg = f"🎯 تقرير: {name}\n💰 السعر: {p:.2f}\n⭐ التقييم: {score}/6\n🚀 هدف: {res:.2f}\n🛡️ دعم: {sup:.2f}\n📊 سيولة: {vol:.1f}M"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    st.markdown(f"""
    <div class="report-card">
        <h2 style="text-align:center;">{name} ({sym})</h2>
        <div style="display:flex; justify-content:space-around; margin:20px 0;">
            <div class="metric-box">💰 السعر<br><b>{p:.3f}</b></div>
            <div class="metric-box">⭐ التقييم<br><b>{score}/6</b></div>
            <div class="metric-box">📊 السيولة<br><b>{vol:.1f}M</b></div>
        </div>
        
        <div style="background:#0d1117; padding:15px; border-radius:10px; border:1px dashed #30363d;">
            <p style="text-align:center; color:#3498db; font-weight:bold;">🔍 فحص المؤشرات الذكي:</p>
            <div style="display:flex; justify-content:space-between; font-size:14px;">
                <span>📈 فوق متوسط 50: <b class="{'indicator-on' if cond1 else 'indicator-off'}">{'نعم ✅' if cond1 else 'لا ⚠️'}</b></span>
                <span>💧 زخم السيولة (MACD): <b class="{'indicator-on' if cond2 else 'indicator-off'}">{'إيجابي ✅' if cond2 else 'سلبي ⚠️'}</b></span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:14px; margin-top:10px;">
                <span>📟 قوة الشراء (RSI): <b>{rsi:.1f}</b></span>
                <span>🔥 اتجاه السعر: <b class="{'indicator-on' if cond4 else 'indicator-off'}">{'صاعد ✅' if cond4 else 'هابط ⚠️'}</b></span>
            </div>
        </div>

        <div style="margin-top:20px;">
            <p>🚀 <b>المقاومة (هدف 20 يوم):</b> <span style="color:#3498db; font-size:18px;">{res:.3f}</span></p>
            <p>🛡️ <b>الدعم (أمان 20 يوم):</b> <span style="color:#3498db; font-size:18px;">{sup:.3f}</span></p>
            <p style="text-align:center; color:#ff3b30; font-weight:bold;">🛑 وقف الخسارة: {sup*0.98:.3f}</p>
        </div>
        
        <a href="{wa_url}" target="_blank" class="wa-button">📲 إرسال التحليل الذكي للواتساب</a>
    </div>
    """, unsafe_allow_html=True)

if u_input:
    data = load_smart_data(u_input)
    if not data.empty:
        build_visual_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, data)
    else:
        st.error("الرمز غير صحيح أو لا توجد بيانات")
