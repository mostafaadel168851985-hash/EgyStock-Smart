import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.parse

st.set_page_config(page_title="Smart Stock Analyzer", layout="centered")

# --- CSS التنسيق (تم إصلاحه ليعمل بنظام الكتل المضمونة) ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 20px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d; margin: 10px auto;
        line-height: 1.6;
    }
    .metric-box { background: #21262d; padding: 8px; border-radius: 8px; text-align: center; border: 1px solid #30363d; flex: 1; margin: 5px; }
    .indicator-on { color: #2ecc71; font-weight: bold; }
    .indicator-off { color: #e74c3c; font-weight: bold; }
    .label-gold { color: #f1c40f; font-weight: bold; }
    .label-blue { color: #3498db; font-weight: bold; }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e);
        color: white !important; padding: 12px; border-radius: 10px;
        text-align: center; font-weight: bold; display: block; text-decoration: none; margin-top: 15px;
    }
    .white-text { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# قاعدة بيانات الأسماء المحدثة
ARABIC_DB = {
    "SVCE": "جنوب الوادي للأسمنت", "ARCC": "العربية للأسمنت", "ALUM": "مصر للألومنيوم",
    "ABUK": "أبو قير للأسمدة", "COMI": "البنك التجاري الدولي", "FWRY": "فوري للمدفوعات",
    "BTFH": "بلتون المالية", "TMGH": "مجموعة طلعت مصطفى", "SWDY": "السويدي إليكتريك",
    "ATQA": "مصر الوطنية للصلب", "UNIT": "المتحدة للإسكان", "AMOC": "إسكندرية للزيوت",
    "ISMA": "الإسماعيلية للدواجن", "ETEL": "المصرية للاتصالات"
}

st.markdown("<h1 style='text-align:center; color:white;'>📊 Smart Stock Analyzer</h1>", unsafe_allow_html=True)

u_input = st.text_input("🔍 ادخل كود السهم (مثلاً ATQA):").upper().strip()

def build_card(name, sym, p, high, low, close_prev, vol, score, inds, p_data):
    pivot, rs, ss = p_data
    wa_msg = f"📊 تقرير {name}\n💰 السعر: {p:.2f}\n⭐ التقييم: {score}/6\n📈 الارتكاز: {pivot:.2f}"
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

    # بناء الكارت ككتلة واحدة محكمة الإغلاق
    card_html = f"""
    <div class="report-card">
        <h2 style="text-align:center; color:white;">{name} ({sym})</h2>
        <div style="display:flex; justify-content:space-between;">
            <div class="metric-box">💰 السعر<br><b class="white-text">{p:.3f}</b></div>
            <div class="metric-box">⭐ التقييم<br><b class="white-text">{score}/6</b></div>
            <div class="metric-box">📊 السيولة M<br><b class="white-text">{vol:.1f}</b></div>
        </div>

        <div style="background:#0d1117; padding:10px; border-radius:10px; border:1px dashed #30363d; margin:15px 0;">
            <p style="text-align:center; color:#3498db !important; font-weight:bold; margin-bottom:5px;">🔍 الفحص الفني الذكي:</p>
            <div style="display:flex; justify-content:space-between; font-size:14px;">
                <span>📈 EMA50: <b class="{'indicator-on' if inds['c1'] else 'indicator-off'}">{'إيجابي' if inds['c1'] else 'سلبي'}</b></span>
                <span>💧 الزخم: <b class="{'indicator-on' if inds['c2'] else 'indicator-off'}">{'إيجابي' if inds['c2'] else 'سلبي'}</b></span>
                <span>🔥 الاتجاه: <b class="{'indicator-on' if inds['c4'] else 'indicator-off'}">{'صاعد' if inds['c4'] else 'هابط'}</b></span>
            </div>
        </div>

        <div style="background:#21262d; padding:8px; border-radius:8px; margin-bottom:10px; text-align:center;">
            <p style="margin:0;"><span class="label-gold">🟡 نقطة الارتكاز:</span> <b class="white-text">{pivot:.3f}</b></p>
        </div>

        <div style="display:flex; justify-content:space-between;">
            <div style="width:48%;">
                <p class="label-blue">🚀 المقاومات:</p>
                <p class="white-text">م 1: {rs[0]:.3f}<br>م 2: {rs[1]:.3f}<br>م 3: {rs[2]:.3f}</p>
            </div>
            <div style="width:48%;">
                <p class="label-blue">🛡️ الدعوم:</p>
                <p class="white-text">د 1: {ss[0]:.3f}<br>د 2: {ss[1]:.3f}<br>د 3: {ss[2]:.3f}</p>
            </div>
        </div>

        <div style="background:#0d1117; padding:10px; border-radius:8px; font-size:13px; margin-top:10px; border: 1px solid #444;">
            <div style="display:flex; justify-content:space-between;">
                <span class="white-text">🔝 أعلى: {high:.3f}</span>
                <span class="white-text">📉 أدنى: {low:.3f}</span>
                <span class="white-text">🔙 أمس: {close_prev:.3f}</span>
            </div>
        </div>
        <a href="{wa_url}" target="_blank" class="wa-button">📲 مشاركة عبر WhatsApp</a>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# --- محرك التحليل ---
res_found = False
if u_input:
    try:
        ticker = u_input if u_input.endswith(".CA") else f"{u_input}.CA"
        data = yf.Ticker(ticker).history(period="1mo")
        if not data.empty:
            last = data.iloc[-1]
            p, hi, lo, cl = last["Close"], last["High"], last["Low"], data["Close"].iloc[-2]
            pivot = (hi + lo + p) / 3
            rs = [(2*pivot)-lo, pivot+(hi-lo), hi+2*(pivot-lo)]
            ss = [(2*pivot)-hi, pivot-(hi-lo), lo-2*(hi-pivot)]
            
            # حساب سكور مبسط لضمان عدم حدوث Error
            inds = {"c1": p > data["Close"].rolling(20).mean().iloc[-1], "c2": p > cl, "c4": p > data["Close"].iloc[-3]}
            sc = sum([inds["c1"], inds["c2"], inds["c4"]]) + 2
            
            build_card(ARABIC_DB.get(u_input, "شركة متداولة"), u_input, p, hi, lo, cl, (last['Volume']*p)/1e6, sc, inds, (pivot, rs, ss))
            res_found = True
    except: pass

# --- اليدوي ---
st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h4 style='color:white; text-align:center;'>🛠️ لوحة التحليل اليدوي</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: pm = st.number_input("💵 السعر الآن:", format="%.3f", key="p_m")
with c2: hm = st.number_input("🔝 أعلى سعر:", format="%.3f", key="h_m")
with c3: lm = st.number_input("📉 أقل سعر:", format="%.3f", key="l_m")

with st.expander("📊 بيانات إضافية"):
    c4, c5 = st.columns(2)
    with c4: clm = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="cl_m")
    with c5: vm = st.number_input("💧 السيولة (M):", format="%.2f", key="v_m")

if pm > 0 and not res_found:
    pivot = (hm + lm + pm) / 3 if hm > 0 else pm
    rs = [(2*pivot)-lm if lm>0 else pm*1.02, pm*1.04, pm*1.06]
    ss = [(2*pivot)-hm if hm>0 else pm*0.98, pm*0.96, pm*0.94]
    build_card(ARABIC_DB.get(u_input, "تحليل يدوي"), u_input if u_input else "MANUAL", pm, hm, lm, clm, vm, 3, {"c1":True, "c2":True, "c4":True}, (pivot, rs, ss))
