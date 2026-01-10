import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="EGX Ultimate Sniper", layout="centered")

# --- CSS التنسيق الاحترافي ---
st.markdown("""
    <style>
    header, .main, .stApp {background-color: #0d1117 !important;}
    .whatsapp-card {
        background-color: #1e2732; color: white; padding: 25px; border-radius: 15px; 
        direction: rtl; text-align: right; border: 1px solid #30363d;
        max-width: 450px; margin: 10px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .section-title { color: #3498db; font-weight: bold; border-bottom: 1px solid #333; margin: 15px 0 10px 0; padding-bottom: 5px; font-size: 18px; }
    .price-val { font-weight: bold; font-family: monospace; font-size: 19px; color: #4cd964; }
    .info-line { font-size: 16px; margin: 8px 0; }
    .wa-link {
        background: linear-gradient(45deg, #25d366, #128c7e); color: white !important; 
        padding: 15px; border-radius: 50px; text-align: center; font-weight: bold;
        display: block; text-decoration: none; margin: 20px auto; max-width: 280px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.05);} 100% {transform: scale(1);} }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🎯 رادار القناص المحترف</h1>", unsafe_allow_html=True)
u_input = st.text_input("🔍 ادخل الرمز (مثل ATQA):").upper()

# --- لوحة التحليل اليدوي المزدوج ---
st.markdown("<h3 style='color:white; text-align:center;'>🛠️ لوحة الإدخال اليدوي الشاملة</h3>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: m_p = st.number_input("💵 السعر الآن:", value=0.0, format="%.3f", key="p1")
with c2: m_h = st.number_input("🔝 أعلى سعر اليوم:", value=0.0, format="%.3f", key="p2")
with c3: m_l = st.number_input("📉 أقل سعر اليوم:", value=0.0, format="%.3f", key="p3")

c4, c5, c6 = st.columns(3)
with c4: m_cl = st.number_input("↩️ إغلاق أمس:", value=0.0, format="%.3f", key="p4")
with c5: m_mh = st.number_input("🗓️ أعلى سعر شهر:", value=0.0, format="%.3f", key="p5")
with c6: m_v = st.number_input("💧 سيولة اليوم (M):", value=0.0, format="%.2f", key="p6")

# تفعيل الكارت بمجرد وجود البيانات الأساسية
if m_p > 0 and m_h > 0 and m_l > 0:
    # حسابات المضارب
    piv = (m_h + m_l + m_p) / 3
    r1, r2 = (2 * piv) - m_l, piv + (m_h - m_l)
    s1 = (2 * piv) - m_h
    
    # حسابات المستثمر
    inv_target = m_mh * 1.15 if m_mh > 0 else m_p * 1.20
    trend_status = "إيجابي 🔥" if m_p > m_cl and m_p > piv else "مراقبة ⚖️"

    st.markdown(f"""
    <div class="whatsapp-card">
        <div style="font-size:22px; text-align:center; font-weight:bold;">💎 تقرير {u_input if u_input else 'السهم'} الشامل</div>
        <div style="text-align:center; font-size:14px; opacity:0.8;">تحليل يدوي (مضارب + مستثمر)</div>
        <div class="separator" style="border-top:2px solid white; margin:15px 0;"></div>
        
        <div class="info-line">💰 السعر الحالي: <span class="price-val">{m_p:.3f}</span></div>
        <div class="info-line">📊 حالة السهم: <b>{trend_status}</b></div>
        
        <div class="section-title">🏹 قسم المضارب اللحظي</div>
        <div class="info-line">📍 نقطة الارتكاز: <b>{piv:.3f}</b></div>
        <div class="info-line">🚀 أهداف المضارب: <b>{r1:.3f} | {r2:.3f}</b></div>
        <div class="info-line">🛡️ دعمك الأساسي: <b>{s1:.3f}</b></div>
        
        <div class="section-title">🏢 قسم المستثمر (متوسط)</div>
        <div class="info-line">🎯 هدف المستثمر: <span style="color:#3498db; font-weight:bold;">{inv_target:.3f}</span></div>
        <div class="info-line">🔝 القمة الشهرية: <b>{m_mh if m_mh > 0 else 'غير محددة'}</b></div>
        <div class="info-line">💧 السيولة المرصودة: <b>{m_v:.1f} مليون</b></div>
        
        <div class="separator" style="border-top:1px solid #555; margin:15px 0;"></div>
        <div class="info-line" style="text-align:center; width:100%; display:block;">🛑 وقف الخسارة النهائي: <span style="color:#ff3b30; font-weight:bold;">{s1*0.98:.3f}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # رسالة الواتساب الشاملة
    m_msg = f"🎯 تحليل {u_input}%0A💰 السعر: {m_p:.3f}%0A🏹 للمضارب: هدف {r1:.3f} - ارتكاز {piv:.3f}%0A🏢 للمستثمر: هدف {inv_target:.3f}%0A🛑 وقف: {s1*0.98:.3f}"
    st.markdown(f'<a href="https://wa.me/?text={m_msg}" target="_blank" class="wa-link">🚀 مشاركة التقرير الشامل</a>', unsafe_allow_html=True)

st.caption("EGX Ultimate Sniper v15.0 | Investor & Trader Edition")
