import asyncio
import json
import streamlit as st
import websockets
import threading
from streamlit_autorefresh import st_autorefresh

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Ombuor Matches Tool Pro", layout="wide")
st.title("📊 Ombuor Matches Tool Pro")

# Automatically refresh the browser UI every 1000 milliseconds (1 second)
st_autorefresh(interval=1000, key="datarefresh")

# Layout Columns
col_metrics, col_chart = st.columns(2)

with col_metrics:
    ticker_box = st.empty()
    stats_box = st.empty()

with col_chart:
    heatmap_box = st.empty()

# --- Shared Memory Storage ---
# We use st.session_state so memory persists across automatic page refreshes
if "digit_counts" not in st.session_state:
    st.session_state.digit_counts = {str(i): 0 for i in range(10)}
if "total_ticks" not in st.session_state:
    st.session_state.total_ticks = 0
if "latest_price" not in st.session_state:
    st.session_state.latest_price = "0.00"
if "latest_digit" not in st.session_state:
    st.session_state.latest_digit = "Waiting..."

def render_ui_dashboard():
    """Reads the current shared state and draws it on the screen."""
    latest_price = st.session_state.latest_price
    latest_digit = st.session_state.latest_digit
    total = st.session_state.total_ticks
    
    ticker_box.metric(
        label="Volatility 100 Index (R_100) Live Price", 
        value=f"${latest_price}", 
        delta=f"Latest Digit: {latest_digit}"
    )
    
    stats_html = "### Live Digit Statistics\n"
    stats_html += f"**Total Samples Tracked:** {total}\n\n"
    
    for digit in sorted(st.session_state.digit_counts.keys()):
        count = st.session_state.digit_counts[digit]
        percentage = (count / total * 100) if total > 0 else 0.0
        
        bar_length = int(percentage // 2)
        visual_bar = "█" * bar_length
        
        stats_html += f"**[{digit}]** `{count:<5}` ({percentage:>5.1f}%) {visual_bar}\n\n"
        
    stats_box.markdown(stats_html)
    heatmap_box.info(f"Analyzing market stability patterns... Last calculated index cluster hit: Digit [{latest_digit}]")

# --- Asynchronous Deriv Networking Stream ---
async def fetch_live_market_data(state_reference):
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
                                # Save directly into the reference container
                                state_reference["digit_counts"][last_digit] += 1
                                state_reference["total_ticks"] += 1
                                state_reference["latest_price"] = price_str
                                state_reference["latest_digit"] = last_digit
                                
        except (websockets.exceptions.ConnectionClosed, Exception):
            await asyncio.sleep(3)
            continue

def start_websocket_thread(state_reference):
    """Runs the asyncio websocket loop safely inside a background thread context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_live_market_data(state_reference))

# --- Main Runtime Loop Execution ---
if __name__ == "__main__":
    # Create a stable global reference link that our background thread can always talk to
    if "global_ref" not in st.session_state:
        st.session_state.global_ref = {
            "digit_counts": st.session_state.digit_counts,
            "total_ticks": st.session_state.total_ticks,
            "latest_price": st.session_state.latest_price,
            "latest_digit": st.session_state.latest_digit
        }
        
    thread_exists = any(t.name == "DerivDataStreamPro" for t in threading.enumerate())
    
    if not thread_exists:
        bg_thread = threading.Thread(
            target=start_websocket_thread, 
            args=(st.session_state.global_ref,), 
            name="DerivDataStreamPro", 
            daemon=True
        )
        bg_thread.start()
        
    # Re-draw layout components based on latest background values
    render_ui_dashboard()
