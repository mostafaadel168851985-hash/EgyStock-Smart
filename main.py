import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Liquidity Radar", page_icon="🌊")

# 1. ستايل الواجهة
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #000000 !important;}
    .report-card { background: white; padding: 25px; border-radius: 15px; color: black; direction: rtl; text-align: right; border-right: 10px solid #1a73e8; }
    .manual-box { background: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #1a73e8; color: white; margin-bottom: 20px;}
    .price-val { font-size: 55px; color: #d32f2f; font-weight: 900; line-height: 1; }
    .metric-box { background: #f8f9fa; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# 2. وظيفة تحليل السيولة المقارن
def analyze_liquidity(today, yesterday, avg_month):
    status = "طبيعية ⚖️"
    color = "black"
    advice = "السيولة في مستوياتها العادية."
    
    if today > yesterday and today > avg_month:
        status = "اختراق سيولة (دخول مؤسسات) 🐳🔥"
        color = "green"
        advice = "إشارة قوية: السهم يشهد تجميعاً ملحوظاً اليوم!"
    elif today < yesterday * 0.5:
        status = "ضعف حاد في التنفيذ ⚠️"
        color = "red"
        advice = "حذر: السهم يفتقد للزخم، قد يكون الصعود وهمياً."
    elif today > avg_month * 1.5:
        status = "سيولة غير اعتيادية ✨"
        color = "#1a73e8"
        advice = "لفت انتباه: هناك حركة غير طبيعية على السهم مقارنة بالشهر الماضي."
        
    return {"status": status, "color": color, "advice": advice}

st.markdown('<h2 style="color:white; text-align:center;">🌊 رادار السيولة والتحليل الرقمي</h2>', unsafe_allow_html=True)

u_input = st.text_input("🔍 ادخل رمز السهم (مثلاً CRST):", "").strip().upper()

if u_input:
    st.markdown(f'<div class="manual-box">📊 تحليل يدوي متقدم لسهم <b>{u_input}</b></div>', unsafe_allow_html=True)
    
    # تقسيم المدخلات
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1: curr_p = st.number_input("السعر الحالي:", format="%.3f")
    with col_p2: high_p = st.number_input("أعلى سعر:", format="%.3f")
    with col_p3: low_p = st.number_input("أقل سعر:", format="%.3f")
    
    st.markdown("---")
    st.write("💰 **مقارنة قيم التداول (بالمليون ج.م):**")
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1: vol_today = st.number_input("سيولة اليوم:", format="%.2f")
    with col_v2: vol_yesterday = st.number_input("سيولة أمس:", format="%.2f")
    with col_v3: vol_month = st.number_input("متوسط الشهر:", format="%.2f")
    
    if curr_p > 0 and vol_today > 0:
        liq_res = analyze_liquidity(vol_today, vol_yesterday, vol_month)
        
        # معادلة الأهداف الرقمية
        pivot = (curr_p + high_p + low_p) / 3
        r1 = (2 * pivot) - low_p
        
        st.markdown(f"""
        <div class="report-card">
            <h3>📊 نتيجة تحليل {u_input}</h3>
            <span class="price-val">{curr_p:.3f}</span>
            <div style="margin: 15px 0;">
                <b style="color:{liq_res['color']}; font-size:20px;">{liq_res['status']}</b><br>
                <i style="color:gray;">{liq_res['advice']}</i>
            </div>
            <hr>
            <div style="display: flex; justify-content: space-around;">
                <div class="metric-box"><b>الهدف الأول</b><br><span style="color:green;">{r1:.3f}</span></div>
                <div class="metric-box"><b>نقطة الارتكاز</b><br><span>{pivot:.3f}</span></div>
                <div class="metric-box"><b>الهدف الثاني</b><br><span style="color:green;">{pivot + (high_p - low_p):.3f}</span></div>
            </div>
            <hr>
            <p style="text-align:center; font-weight:bold; color:#d32f2f;">🛑 وقف الخسارة (إغلاق تحت): {(2 * pivot) - high_p:.3f}</p>
        </div>
        """, unsafe_allow_html=True)
