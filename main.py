import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper v34", layout="centered")

# --- CSS التنسيق النهائي الموحد ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .report-card {
        background-color: #1e2732; color: white; padding: 22px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        margin: 15px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .separator { border-top: 1px solid #444; margin: 12px 0; }
    .price-large { font-weight: bold; font-size: 38px; color: #4cd964; text-align: center; display: block; }
    .label-blue { color: #3498db; font-weight: bold; font-size: 17px; margin-bottom: 5px; }
    .info-line { margin: 8px 0; font-size: 15px; display: flex; justify-content: space-between; }
    .liquidity-box { 
        background: #2d333b; padding: 12px; border-radius: 10px; 
        text-align: center; margin: 10px 0; border: 1px dashed #444; 
    }
    .wa-button {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 12px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- قاموس الأسماء الشامل (تم تحديثه من ملفك الـ PDF) ---
ARABIC_NAMES = {
    "AALR": "العامة لاستصلاح الأراضي", "ABUK": "أبو قير للأسمدة", "ACAMD": "العربية لإدارة الأصول",
    "ACAP": "ايه كابيتال القابضة", "ACGC": "العربية لحليج الأقطان", "ADIB": "مصرف أبو ظبي الإسلامي",
    "AFDI": "الأهلي للتنمية والاستثمار", "ALCN": "الاسكندرية لتداول الحاويات", "AMOC": "الاسكندرية للزيوت المعدنية",
    "ANFI": "الاسكندرية للخدمات الطبية", "ARCC": "العربية للأسمنت", "ASCM": "أسيك للتعدين",
    "ATQA": "مصر الوطنية للصلب - عتاقة", "AUTO": "جي بي أوتو", "BINV": "بي انفستمنتس القابضة",
    "BTFH": "بلتون المالية القابضة", "COMI": "البنك التجاري الدولي", "DAPH": "المطورون العرب",
    "DGTD": "ديجيتال فارما", "DICE": "دايس للملابس", "EAST": "الشرقية - ايسترن كومباني",
    "EKHO": "القابضة المصرية الكويتية", "ETEL": "المصرية للاتصالات", "FWRY": "فوري للمدفوعات",
    "HELI": "مصر الجديدة للاسكان", "ISMA": "الاسماعيلية للدواجن", "JUFO": "جهينة للصناعات الغذائية",
    "MFOT": "مصر لإنتاج الأسمدة - موبكو", "MOED": "المصرية لنظم التعليم الحديث", "ORAS": "أوراسكوم كونستراكشون",
    "PHAR": "الاسكندرية للأدوية", "PHDC": "بالم هيلز للتعمير", "SWDY": "السويدي إليكتريك",
    "TMGH": "مجموعة طلعت مصطفى", "UNIT": "المتحدة للاسكان", "UPMS": "الاتحاد الصيدلي"
}

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المصري</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثلاً SWDY أو ABUK):").upper()

# --- 1. التحليل الآلي اللحظي ---
if u_input:
    try:
        symbol = f"{u_input}.CA"
        df = yf.Ticker(symbol).history(period="150d")
        if not df.empty:
            p = df['Close'].iloc[-1]
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            vol_val = (df['Volume'].iloc[-1] * p) / 1_000_000
            name_ar = ARABIC_NAMES.get(u_input, "شركة متداولة")
            
            # منطق التوصية الآلي
            rec_auto = "احتفاظ ⚖️"
            if rsi < 35: rec_auto = "شراء / تجميع 🟢"
            elif rsi > 70: rec_auto = "جني أرباح ⚠️"

            st.markdown(f"""
            <div class="report-card">
                <div style="text-align:center;"><span style="color:#3498db; font-size:14px;">💎 التحليل الآلي لـ {u_input}</span><br><b style="font-size:22px;">{name_ar}</b></div>
                <div class="separator"></div>
                <div class="info-line"><span>💰 السعر المعتمد:</span> <b>{p:.3f} ج.م</b></div>
                <div class="info-line"><span>📟 مؤشر RSI:</span> <b>{rsi:.1f}</b></div>
                <div class="liquidity-box">
                    <span style="color:#8b949e; font-size:13px;">📊 مبلغ السيولة اللحظي:</span><br>
                    <b style="font-size:22px; color:#4cd964;">{vol_val:.2f} مليون</b><br>
                    <span style="color:#8b949e;">نبض السيولة: {'طبيعية ⚖️' if vol_val > 10 else 'ضعيفة ⚠️'}</span>
                </div>
                <div class="info-line"><span>📢 التوصية الفنية:</span> <b>{rec_auto}</b></div>
                <div class="separator"></div>
                <div class="label-blue">🚀 مستويات المقاومة: <b>{p*1.025:.3f} | {p*1.05:.3f}</b></div>
                <div class="label-blue">🛡️ مستويات الدعم: <b>{p*0.975:.3f} | {p*0.95:.3f}</b></div>
                <div class="separator"></div>
                <div class="label-blue">🏹 قسم المضارب والمستثمر:</div>
                <div class="info-line"><span>🚀 هدف مضاربي: <b>{p*1.03:.3f}</b></span> <span>🎯 هدف مستثمر (+20%): <b>{p*1.20:.3f}</b></span></div>
                <div class="separator"></div>
                <div style="color:#ff3b30; text-align:center; font-weight:bold;">🛑 وقف الخسارة: {p*0.94:.3f}</div>
            </div>
            """, unsafe_allow_html=True)
    except: pass

st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة القناص اليدوية</h3>", unsafe_allow_html=True)

# --- 2. التحليل اليدوي المبسط والذكي ---
c1, c2, c3 = st.columns(3)
with c1: m_p = st.number_input("💵 السعر الآن:", format="%.3f", key="man_p")
with c2: m_h = st.number_input("🔝 أعلى سعر:", format="%.3f", key="man_h")
with c3: m_l = st.number_input("📉 أقل سعر:", format="%.3f", key="man_l")

c4, c5, c6 = st.columns(3)
with c4: m_close = st.number_input("↩️ إغلاق أمس:", format="%.3f", key="man_c")
with c5: m_mhigh = st.number_input("🗓️ أعلى شهر:", format="%.3f", key="man_mh")
with c6: m_vol = st.number_input("💧 السيولة (بالمليون):", format="%.2f", key="man_v")

if m_p > 0:
    name_man = ARABIC_NAMES.get(u_input if u_input else "", "تحليل يدوي")
    # منطق التوصية اليدوي (سعر + سيولة)
    if m_p > m_close:
        rec_man = "شراء قوي 🟢" if m_vol > 10 else "صعود حذر ⚠️"
    else:
        rec_man = "تخارج / سلبي 🔴" if m_vol > 15 else "هدوء / تجميع ⚖️"

    st.markdown(f"""
    <div class="report-card" style="border-right: 8px solid #3498db;">
        <div style="text-align:center;"><span style="color:#3498db;">🛠️ التقرير اليدوي لـ {u_input if u_input else '---'}</span><br><b style="font-size:22px;">{name_man}</b></div>
        <div class="separator"></div>
        <div class="info-line"><span>💰 السعر الحالي:</span> <b>{m_p:.3f}</b></div>
        <div class="liquidity-box">
            <span style="color:#8b949e; font-size:13px;">📊 مبلغ السيولة المدخل:</span><br>
            <b style="font-size:22px; color:#e1e4e8;">{m_vol:.2f} مليون ج.م</b>
        </div>
        <div class="info-line"><span>📢 التوصية الذكية:</span> <b>{rec_man}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🚀 مستويات المقاومة: <b>{m_p*1.025:.3f} | {m_p*1.05:.3f}</b></div>
        <div class="label-blue">🛡️ مستويات الدعم: <b>{m_p*0.975:.3f} | {m_p*0.95:.3f}</b></div>
        <div class="separator"></div>
        <div class="label-blue">🏹 قسم المضارب والمستثمر:</div>
        <div class="info-line"><span>🚀 هدف مضاربي: <b>{m_p*1.03:.3f}</b></span> <span>🎯 هدف مستثمر: <b>{m_p*1.20:.3f}</b></span></div>
        <div class="info-line"><span>🗓️ قمة شهرية: <b>{m_mhigh:.3f}</b></span> <span>🔙 إغلاق أمس: <b>{m_close:.3f}</b></span></div>
        <div style="color:#ff3b30; text-align:center; font-weight:bold; margin-top:10px;">🛑 وقف الخسارة: {m_p*0.94:.3f}</div>
    </div>
    """, unsafe_allow_html=True)
