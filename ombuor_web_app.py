import asyncio
import json
import os
import threading
import time
import streamlit as st

# --- Configuration & File Database ---
DATA_FILE = "market_state.json"

def load_stored_data():
    """Reads current market counters safely from a text database file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "digit_counts": {str(i): 0 for i in range(10)},
        "total_ticks": 0,
        "latest_price": "0.00",
        "latest_digit": "Waiting..."
    }

def save_stored_data(data):
    """Saves live market ticks instantly to a text database file."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

# --- Background Network Stream Engine ---
async def fetch_websocket_ticks():
    """Runs a public unauthenticated WebSocket data capture channel."""
    uri = "wss://://derivws.com"
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                # Subscribe payload targeting Volatility 100 Index (R_100)
                await websocket.send(json.dumps({"ticks": "R_100"}))
                
                async for message in websocket:
                    response = json.loads(message)
                    if response.get("msg_type") == "tick":
                        tick = response.get("tick", {})
                        price = tick.get("quote")
                        
                        if price is not None:
                            price_str = str(price)
                            last_digit = price_str[-1]
                            
                            if last_digit.isdigit():
                                # Read current counts, increment, and commit back to disk
                                current_state = load_stored_data()
                                current_state["digit_counts"][last_digit] += 1
                                current_state["total_ticks"] += 1
                                current_state["latest_price"] = price_str
                                current_state["latest_digit"] = last_digit
                                save_stored_data(current_state)
        except Exception:
            await asyncio.sleep(3)

def run_network_thread():
    """Executes the network loop container in an isolated process space."""
    # Import inside thread to prevent container load execution issues
    global websockets
    import websockets
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_websocket_ticks())

# --- Launch Background Process Engine ---
# Check if the stream thread is alive, if not start it up instantly
if not any(t.name == "DerivDataWorkerEngine" for t in threading.enumerate()):
    # Initialize basic empty cache file on clean boot setup
    if not os.path.exists(DATA_FILE):
        save_stored_data({
            "digit_counts": {str(i): 0 for i in range(10)},
            "total_ticks": 0,
            "latest_price": "0.00",
            "latest_digit": "Waiting..."
        })
    worker = threading.Thread(target=run_network_thread, name="DerivDataWorkerEngine", daemon=True)
    worker.start()

# --- Streamlit Dashboard Front-End Render Layout ---
st.set_page_config(page_title="Ombuor Matches Tool Pro", layout="wide")
st.title("📊 Ombuor Matches Tool Pro")

# Quick button row for manual refreshing
if st.button("🔄 Refresh Data Feed"):
    st.rerun()

# Read from our text database link
market_data = load_stored_data()
total_ticks = market_data["total_ticks"]
latest_price = market_data["latest_price"]
latest_digit = market_data["latest_digit"]
digit_counts = market_data["digit_counts"]

# Structural interface splitting
col_metrics, col_chart = st.columns(2)

with col_metrics:
    st.metric(
        label="Volatility 100 Index (R_100) Live Price", 
        value=f"${latest_price}", 
        delta=f"Latest Digit: {latest_digit}"
    )
    
    st.markdown("### Live Digit Statistics")
    st.write(f"**Total Samples Tracked:** {total_ticks}")
    
    # Compute horizontal visual layout progress rows
    for digit in sorted(digit_counts.keys()):
        count = digit_counts[digit]
        percentage = (count / total_ticks * 100) if total_ticks > 0 else 0.0
        
        # Calculate block repetition multipliers
        bar_length = int(percentage // 2)
        visual_bar = "█" * bar_length
        
        st.markdown(f"**[{digit}]** `{count:<5}` ({percentage:>5.1f}%) {visual_bar}")

with col_chart:
    st.info(f"Analyzing market stability patterns... Last calculated index cluster hit: Digit [{latest_digit}]")
