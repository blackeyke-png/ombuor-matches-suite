import asyncio
import json
import streamlit as st
import websockets
import threading

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Ombuor Matches Tool Pro", layout="wide")
st.title("📊 Ombuor Matches Tool Pro")

# Layout Columns
col_metrics, col_chart = st.columns(2)

with col_metrics:
    ticker_box = st.empty()
    stats_box = st.empty()

with col_chart:
    heatmap_box = st.empty()

# --- Global Market Counters ---
if "digit_counts" not in st.session_state:
    st.session_state.digit_counts = {str(i): 0 for i in range(10)}
if "total_ticks" not in st.session_state:
    st.session_state.total_ticks = 0

def render_ui_dashboard(latest_digit, latest_price):
    """Dynamically updates the Streamlit interface elements with text-based bars."""
    ticker_box.metric(
        label="Volatility 100 Index (R_100) Live Price", 
        value=f"${latest_price}", 
        delta=f"Latest Digit: {latest_digit}"
    )
    
    stats_html = "### Live Digit Statistics\n"
    stats_html += f"**Total Samples Tracked:** {st.session_state.total_ticks}\n\n"
    
    for digit in sorted(st.session_state.digit_counts.keys()):
        count = st.session_state.digit_counts[digit]
        total = st.session_state.total_ticks
        percentage = (count / total * 100) if total > 0 else 0.0
        
        bar_length = int(percentage // 2)
        visual_bar = "█" * bar_length
        
        stats_html += f"**[{digit}]** `{count:<5}` ({percentage:>5.1f}%) {visual_bar}\n\n"
        
    stats_box.markdown(stats_html)
    heatmap_box.info(f"Analyzing market stability patterns... Last calculated index cluster hit: Digit [{latest_digit}]")

# --- Asynchronous Deriv Networking ---
async def fetch_live_market_data():
    uri = "wss://://derivws.com"
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                sub_req = {"ticks": "R_100"}
                await websocket.send(json.dumps(sub_req))
                
                async for message in websocket:
                    data = json.loads(message)
                    
                    if data.get("msg_type") == "tick":
                        tick_info = data.get("tick", {})
                        price = tick_info.get("quote")
                        
                        if price is not None:
                            price_str = str(price)
                            last_digit = price_str[-1]
                            
                            if last_digit.isdigit():
                                st.session_state.digit_counts[last_digit] += 1
                                st.session_state.total_ticks += 1
                                render_ui_dashboard(last_digit, price_str)
                                
        except (websockets.exceptions.ConnectionClosed, Exception):
            await asyncio.sleep(3)
            continue

def start_websocket_thread():
    """Runs the asyncio websocket loop safely inside a background thread context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_live_market_data())

# --- Main Runtime Loop Execution ---
if __name__ == "__main__":
    thread_exists = any(t.name == "DerivDataStream" for t in threading.enumerate())
    
    if not thread_exists:
        bg_thread = threading.Thread(target=start_websocket_thread, name="DerivDataStream", daemon=True)
        bg_thread.start()
        
    render_ui_dashboard("Waiting...", "0.00")
