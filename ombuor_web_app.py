# Save this file exactly as: ombuor_web_app.py
import streamlit as st
import random
import time
import pandas as pd
import json
import asyncio
import websockets

# Configure responsive page view parameters
st.set_page_config(page_title="MATCHES TOOL PRO", page_icon="🎯", layout="wide")

# Embedded Premium Web CSS Theme Templates to match reference style
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        background-image: radial-gradient(rgba(29, 38, 113, 0.15) 1px, transparent 0);
        background-size: 24px 24px;
        color: #f1f5f9;
    }
    .portal-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 40px;
        max-width: 480px;
        margin: 0 auto;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .live-badge {
        background-color: #10b981;
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

# SECURITY CREDENTIAL CONFIGURATION 
DEVELOPER_USERNAME = "ombuor"
DEVELOPER_PASSWORD = "money100"
DERIV_API_TOKEN = "pat_cb77c41273d06fc75aa4690791765c3bfb88b42baba27e6fc6ab2c1bde290a29"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "price" not in st.session_state:
    st.session_state.price = 0.0
if "digit_history" not in st.session_state:
    st.session_state.digit_history = []

# --- LAYER 1: CLIENT ACCESS GATEWAY ---
if not st.session_state.authenticated:
    st.markdown("<p style='text-align: center; margin-top: 30px;'><span class='live-badge'>● FEEDS ACTIVE</span> &nbsp; <span style='color:#888; font-size:12px;'>LIVE</span></p>", unsafe_allow_html=True)
    st.markdown("""
        <div class="portal-card">
            <p style="text-align: center; color: #6366f1; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 5px;">Secure Client Portal</p>
            <h2 style="text-align: center; font-size: 32px; font-weight: 700; margin-top: 0px; color: #fff;">Welcome back</h2>
            <p style="text-align: center; color: #9ca3af; font-size: 14px; margin-top: -10px; margin-bottom: 30px;">Sign in to continue to your analytics workspace.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns(3)
    with col_c:
        username = st.text_input("USERNAME", placeholder="Enter your system username")
        access_key = st.text_input("ACCESS KEY", type="password", placeholder="Enter your license access key")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("SIGN IN SECURELY →", use_container_width=True, type="primary"):
            if username.lower() == DEVELOPER_USERNAME and access_key == DEVELOPER_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Signature Key")

# --- LAYER 2: LIVE MARKET DATA PIPELINE ---
else:
    st.markdown("<p style='float: right;'><span class='live-badge'>● LIVE MARKET DATA PIPELINE ONLINE</span></p>", unsafe_allow_html=True)
    st.title("🎯 OMBUOR MATCHES SUITE v3.0")
    if st.button("🔒 Disconnect Terminals"):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown("---")

    col_metrics, col_chart = st.columns(2)
    with col_metrics:
        ticker_box = st.empty()
        stats_box = st.empty()
    with col_chart:
        heatmap_box = st.empty()

    async def fetch_live_market_data():
        url = "wss://://binaryws.com"
        
        async with websockets.connect(url) as websocket:
            auth_req = {"authorize": DERIV_API_TOKEN}
            await websocket.send(json.dumps(auth_req))
            await websocket.recv()
            
            sub_req = {"ticks": "R_100"}
            await websocket.send(json.dumps(sub_req))
            
            while st.session_state.authenticated:
                response = await websocket.recv()
                data = json.loads(response)
                
                if "tick" in data:
                    raw_price = data["tick"]["quote"]
                    st.session_state.price = raw_price
                    
                    str_price = f"{raw_price:.2f}"
                    last_digit = int(str_price[-1])
                    st.session_state.digit_history.append(last_digit)
                    if len(st.session_state.digit_history) > 100:
                        st.session_state.digit_history.pop(0)
                        
                    counts = {d: st.session_state.digit_history.count(d) for d in range(10)}
                    best_match = max(counts, key=counts.get)
                    best_differ = min(counts, key=counts.get)
                    total_ticks = len(st.session_state.digit_history)
                    match_p = round((counts[best_match] / total_ticks) * 100, 1) if total_ticks > 0 else 0
                    differ_p = round((counts[best_differ] / total_ticks) * 100, 1) if total_ticks > 0 else 0

                    with ticker_box.container():
                        st.markdown("### 📈 Live Index Stream (Real Market Data)")
                        m1, m2 = st.columns(2)
                        m1.metric(label="VOLATILITY 100 INDEX (1s)", value=f"${st.session_state.price:,}")
                        m2.metric(label="ISOLATED DECIMAL POSITION", value=f"Digit: [ {last_digit} ]")
                        st.markdown("---")

                    with stats_box.container():
                        st.markdown("### 🔮 Signal Probability Matrix")
                        st.markdown(f"<div style='background: rgba(16,185,129,0.1); padding:15px; border-radius:6px; border-left:5px solid #10b981; margin-bottom:10px;'>⚡ <b>RECOMMENDED MATCH TARGET:</b> Digit <span style='font-size:20px; color:#10b981;'><b>{best_match}</b></span> ({match_p}% historical density)</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='background: rgba(245,158,11,0.1); padding:15px; border-radius:6px; border-left:5px solid #f59e0b;'>🛡️ <b>RECOMMENDED DIFFER SAFETY:</b> Digit <span style='font-size:20px; color:#f59e0b;'><b>{best_differ}</b></span> ({differ_p}% risk profile)</div>", unsafe_allow_html=True)

                    with heatmap_box.container():
                        st.markdown("### 📊 100-Tick Array Heatmap Engine")
                        df = pd.DataFrame({
                            "Digit Parameter": [str(d) for d in range(10)],
                            "Match Ratio (%)": [counts[d] for d in range(10)]
                        })
                        st.bar_chart(data=df, x="Digit Parameter", y="Match Ratio (%)", use_container_width=True)

    # Boot the parallel processing data framework loop cleanly
    asyncio.run(fetch_live_market_data())
