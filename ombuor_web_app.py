import asyncio
import json
import streamlit as st
import websockets

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Ombuor Matches Tool Pro", layout="wide")
st.title("📊 Ombuor Matches Tool Pro")

# Create layout structure
col_metrics, col_chart = st.columns(2)
with col_metrics:
    ticker_box = st.empty()
    stats_box = st.empty()
with col_chart:
    heatmap_box = st.empty()

# --- Initialize Session Storage ---
if "digit_counts" not in st.session_state:
    st.session_state.digit_counts = {str(i): 0 for i in range(10)}
if "total_ticks" not in st.session_state:
    st.session_state.total_ticks = 0

def render_dashboard(latest_price, latest_digit):
    """Draws all elements on the screen immediately when a tick arrives."""
    total = st.session_state.total_ticks
    
    # 1. Update live price box
    ticker_box.metric(
        label="Volatility 100 Index (R_100) Live Price", 
        value=f"${latest_price}", 
        delta=f"Latest Digit: {latest_digit}"
    )
    
    # 2. Build live text bars
    stats_html = "### Live Digit Statistics\n"
    stats_html += f"**Total Samples Tracked:** {total}\n\n"
    
    for digit in sorted(st.session_state.digit_counts.keys()):
        count = st.session_state.digit_counts[digit]
        percentage = (count / total * 100) if total > 0 else 0.0
        
        # Draw text bar length
        bar_length = int(percentage // 2)
        visual_bar = "█" * bar_length
        
        stats_html += f"**[{digit}]** `{count:<5}` ({percentage:>5.1f}%) {visual_bar}\n\n"
        
    stats_box.markdown(stats_html)
    heatmap_box.info(f"Analyzing market stability patterns... Last calculated index cluster hit: Digit [{latest_digit}]")

async def run_live_stream():
    """Establishes a single direct socket channel on Render."""
    uri = "wss://://derivws.com"
    
    # Show initial state while connecting
    render_dashboard("Connecting...", "Waiting")
    
    try:
        async with websockets.connect(uri) as websocket:
            # Send subscription payload for Volatility 100
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
                            # Save data to state
                            st.session_state.digit_counts[last_digit] += 1
                            st.session_state.total_ticks += 1
                            
                            # Immediately update the UI
                            render_dashboard(price_str, last_digit)
                            
    except Exception as e:
        # Reconnect on error or dropouts
        st.write("Stream reconnecting...")
        await asyncio.sleep(2)

# --- Direct execution trigger ---
if __name__ == "__main__":
    # Run the stream directly in the Streamlit application workflow
    asyncio.run(run_live_stream())
