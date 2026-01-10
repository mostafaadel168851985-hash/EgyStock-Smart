import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS التنسيق ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d; margin: 10px auto;
    }
    .metric-box { background: #21262d; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #30363d; }
    .indicator-on { color: #2ecc71; font-weight: bold; }
    .indicator-off { color: #e74c3c; font-weight: bold; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; padding: 12px; border-radius: 10px;
        text-align: center; font-weight: bold; display: block; text-decoration: none; margin-top: 15px;
    }
    .white-text { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- قاعدة بيانات الأسماء (PDF / CSV) ---
# ضع هنا CSV أو PDF جاهز باسماء الشركات + الأكواد
# مثال CSV: Symbol,Name
ARABIC_DB = pd.read_csv("egx_companies.csv").set_index("Symbol")["Name"].to_dict()

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)

# حقل إدخال الكود
u_input = st.text_input("🔍 ادخل كود السهم (مثلاً TMGH):").upper().strip()

# --- دوال جلب البيانات ---
def get_yahoo_data(symbol):
    """ محاولة جلب البيانات من Yahoo Finance """
    try:
        ticker = symbol if symbol.endswith(".CA") else f"{symbol}.CA"
        df = yf.Ticker(ticker).history(period="1y")
        if df.empty or len(df) < 20:
            return None
        return df
    except:
        return None

def get_fallback_data(symbol):
    """ fallback للبيانات من CSV """
    try:
        fallback_df = pd.read_csv("egx_prices.csv")  # CSV فيه الأعمدة: Date,Symbol,Close,High,Low,Volume
        df = fallback_df[fallback_df["Symbol"]==symbol].copy()
        if df.empty:
            return None
        df.index = pd.to_datetime(df["Date"])
        return df
    except:
        return None

def get_stock_data(symbol):
    """ دالة موحدة لجلب البيانات """
    df = get_yahoo_data(symbol)
    if df is None:
        df = get_fallback_data(symbol)
    return df

# --- دالة رسم الكارت ---
def build_card(name, sym, p, vol, rsi, sup, res, score, cl_p=0, m_h=0, h_d=0, l_d=0, is_auto=False, inds=None):
    wa_msg = f"🎯 تقرير: {name}\n💰 السعر: {p:.3f}\n⭐ التقييم: {score}/6\n🚀 هدف: {res:.2f}\n🛡️ دعم: {sup:.2f}"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    st.markdown(f"""
    <div class="report-card">
        <h2 style="text-align:center; color:white; margin-bottom:5px;">{name}</h2>
        <p style="text-align:center; color:#3498db; margin-top:0;">({sym})</p>
        
        <div style="display:flex; justify-content:space-around; margin:10px 0;">
            <div class="metric-box">💰 السعر<br><b class="white-text">{p:.3f}</b></div>
            <div class="metric-box">⭐ التقييم<br><b class="white-text">{score}/6</b></div>
            <div class="metric-box">📊 السيولة M<br><b class="white-text">{vol:.1f}</b></div>
        </div>
    """, unsafe_allow_html=True)

    # فحص المؤشرات الذكي
    if inds:
        st.markdown(f"""
        <div style="background:#0d1117; padding:12px; border-radius:10px; border:1px dashed #30363d; margin-bottom:15px;">
            <p style="text-align:center; color:#3498db; font-weight:bold; margin-bottom:5px;">🔍 الفحص الفني الذكي:</p>
            <div style="display:flex; justify-content:space-between; font-size:14px;">
                <span class="white-text">📈 فوق EMA50: <b class="{'indicator-on' if inds['c1'] else 'indicator-off'}">{'نعم ✅' if inds['c1'] else 'لا ⚠️'}</b></span>
                <span class="white-text">💧 الماكد: <b class="{'indicator-on' if inds['c2'] else 'indicator-off'}">{'إيجابي ✅' if inds['c2'] else 'سلبي ⚠️'}</b></span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:14px; margin-top:8px;">
                <span class="white-text">📟 RSI: <b class="white-text">{rsi:.1f}</b></span>
                <span class="white-text">🔥 الاتجاه: <b class="{'indicator-on' if inds['c4'] else 'indicator-off'}">{'صاعد ✅' if inds['c4'] else 'هابط ⚠️'}</b></span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
        <div style="margin-top:10px;">
            <p><span style="color:#3498db; font-weight:bold;">🚀 المقاومة:</span> <b class="white-text">{res:.3f}</b></p>
            <p><span style="color:#3498db; font-weight:bold;">🛡️ الدعم:</span> <b class="white-text">{sup:.3f}</b></p>
            <p style="text-align:center; color:#ff3b30; font-weight:bold; font-size:18px;">🛑 وقف الخسارة: {sup*0.98:.3f}</p>
        </div>
        
        <div style="background:#21262d; padding:10px; border-radius:8px; font-size:13px; border: 1px solid #30363d;">
            <div style="display:flex; justify-content:space-between;">
                <span class="white-text">🔝 أعلى يوم: <b>{h_d:.3f}</b></span>
                <span class="white-text">📉 أقل يوم: <b>{l_d:.3f}</b></span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:5px;">
                <span class="white-text">🔙 إغلاق أمس: <b>{cl_p:.3f}</b></span>
                <span class="white-text">🗓️ أعلى شهر: <b>{m_h:.3f}</b></span>
            </div>
        </div>
        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة التقرير عبر WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# --- جلب البيانات وتحليلها ---
if u_input:
    df = get_stock_data(u_input)
    if df is not None and len(df) > 20:
        df["EMA50"] = ta.ema(df["Close"], length=50)
        df["RSI"] = ta.rsi(df["Close"], length=14)
        macd_df = ta.macd(df["Close"])
        
        last = df.iloc[-1]
        p, r = last["Close"], last["RSI"]
        v = (last['Volume'] * p) / 1_000_000
        s20, r20 = df["Low"].tail(20).min(), df["High"].tail(20).max()
        
        inds_data = {
            "c1": p > last["EMA50"] if "EMA50" in df and not pd.isna(last["EMA50"]) else False,
            "c2": macd_df.iloc[-1]["MACD_12_26_9"] > macd_df.iloc[-1]["MACDs_12_26_9"] if macd_df is not None else False,
            "c3": r < 60,
            "c4": p > df["Close"].iloc[-2]
        }
        sc = sum([inds_data["c1"], inds_data["c2"], inds_data["c3"], inds_data["c4"]]) + (2 if r < 35 else 0)
        
        build_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, v, r, s20, r20, sc,
                   cl_p=df["Close"].iloc[-2], m_h=df["High"].tail(22).max(),
                   h_d=last["High"], l_d=last["Low"], is_auto=True, inds=inds_data)
    else:
        st.warning("⚠️ البيانات غير متاحة للسهم هذا، يمكنك استخدام الإدخال اليدوي.")

# --- اللوحة اليدوية ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color:white; text-align:center;'>🛠️ لوحة الإدخال اليدوي</h4>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1: p_m = st.number_input("💵 السعر الآن:", format="%.3f", key="p_m")
with col2: h_m = st.number_input("🔝 أعلى اليوم:", format="%.3f", key="h_m")
with col3: l_m = st.number_input("📉 أقل اليوم:", format="%.3f", key="l_m")
col4, col5, col6 = st.columns(3)
with col4: cl_m = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="cl_m")
with col5: mh_m = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="mh_m")
with col6: v_m = st.number_input("💧 السيولة (M):", format="%.2f", key="v_m")

if p_m > 0:
    m_inds = {"c1": p_m > cl_m, "c2": True, "c3": True, "c4": p_m > cl_m}
    build_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL",
               p_m, v_m, 50.0, p_m*0.97, p_m*1.03, 3 if p_m > cl_m else 2,
               cl_p=cl_m, m_h=mh_m, h_d=h_m, l_d=l_m, is_auto=False, inds=m_inds)
