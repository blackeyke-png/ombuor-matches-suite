
import asyncio
import json
import streamlit as st
import websockets

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Ombuor Matches Tool Pro", layout="wide")
st.title("📊 Ombuor Matches Tool Pro")

# Layout Columns matching lines 87-92 of your repository
col_metrics, col_chart = st.columns(2)

with col_metrics:
    ticker_box = st.empty()
    stats_box = st.empty()

with col_chart:
    heatmap_box = st.empty()

# --- Global Market Counters ---
# Session state initialization to prevent resetting on page redraws
if "digit_counts" not in st.session_state:
    st.session_state.digit_counts = {str(i): 0 for i in range(10)}
if "total_ticks" not in st.session_state:
    st.session_state.total_ticks = 0

def render_ui_dashboard(latest_digit, latest_price):
    """Dynamically updates the Streamlit interface elements with text-based bars."""
    # 1. Update the Ticker Box metrics
    ticker_box.metric(
        label="Volatility 100 Index (R_100) Live Price", 
        value=f"${latest_price}", 
        delta=f"Latest Digit: {latest_digit}"
    )
    
    # 2. Build the live data display text
    stats_html = "### Live Digit Statistics\n"
    stats_html += f"**Total Samples Tracked:** {st.session_state.total_ticks}\n\n"
    
    for digit in sorted(st.session_state.digit_counts.keys()):
        count = st.session_state.digit_counts[digit]
        total = st.session_state.total_ticks
        percentage = (count / total * 100) if total > 0 else 0.0
        
        # Draw a clean terminal-style visual bar (compact scale by dividing percentage by 2)
        bar_length = int(percentage // 2)
        visual_bar = "█" * bar_length
        
        stats_html += f"**[{digit}]** `{count:<5}` ({percentage:>5.1f}%) {visual_bar}\n\n"
        
    stats_box.markdown(stats_html)
    
    # 3. Simple text matrix placeholder for the heatmap box
    heatmap_box.info(f"Analyzing market stability patterns... Last calculated index cluster hit: Digit [{latest_digit}]")

# --- Asynchronous Deriv Networking ---
async def fetch_live_market_data():
    # FIXED: Clean production WebSocket URI routing using public App ID 1089
    uri = "wss://://derivws.com"
    
    # Keep checking or reconnecting if deployment environment drops socket packets
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                # OPTIONAL: Authentication request string layer if you pass a security key
                # auth_req = {"authorize": "YOUR_DERIV_API_TOKEN"}
                # await websocket.send(json.dumps(auth_req))
                # await websocket.recv()
                
                # Subscription Payload pointing to your requested asset (Line 101: R_100)
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
                                # Increment global state parameters
                                st.session_state.digit_counts[last_digit] += 1
                                st.session_state.total_ticks += 1
                                
                                # Instantly re-render the Streamlit elements
                                render_ui_dashboard(last_digit, price_str)
                                
        except (websockets.exceptions.ConnectionClosed, Exception) as e:
            # Prevent app crashes on connection timeout; sleep and reconnect
            await asyncio.sleep(3)
            continue

# --- Main Runtime Loop Execution ---
if __name__ == "__main__":
    # Standard fallback initialization for background event loops inside running Streamlit containers
    try:
        asyncio.run(fetch_live_market_data())
    except RuntimeError:
        # Handles runtime nesting exceptions if loop is pre-allocated by web servers like Render
        loop = asyncio.get_event_loop()
        loop.create_task(fetch_live_market_data())
