import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
import hashlib

def check_login(username, password):
    valid_users = {
        "admin": hashlib.md5("password123".encode()).hexdigest()
    }
    
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    return username in valid_users and valid_users[username] == hashed_password

def login_page():
    st.title("🏠 Smart Home Dashboard Login")
    
    st.markdown("""
    <style>
    .stApp {
        font-size: 18px !important;
    }
    .stButton>button {
        width: 100%;
        font-size: 18px !important;
    }
    .stTextInput>div>div>input {
        font-size: 18px !important;
    }
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Set page configuration
st.set_page_config(
    page_title="Smart Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Initialize session state variables
def initialize_session_state():
    defaults = {
        'logged_in': False,
        'temperature': 21.5,
        'humidity': 42,
        'motion': False,
        'lights': {'living': False, 'kitchen': True, 'bedroom': False},
        'thermostat': 22,
        'fan_speed': 0,
        'alerts': [],
        'activity_log': [],
        'last_update': datetime.now().strftime("%H:%M:%S"),
        'security_system': 'disarmed',
        'cameras': {'front_door': True, 'backyard': False, 'garage': False},
        'door_status': {'main': 'closed', 'garage': 'closed', 'back': 'closed'},
        'energy_data': {
            'daily_usage': random.uniform(8, 15),
            'weekly_total': random.uniform(50, 90),
            'monthly_total': random.uniform(180, 250)
        },
        'irrigation_zones': {
            'front_lawn': {'active': False, 'schedule': '06:00 AM', 'duration': 15},
            'backyard': {'active': False, 'schedule': '07:00 AM', 'duration': 20},
            'garden': {'active': False, 'schedule': '05:30 AM', 'duration': 10}
        },
        'current_tab': "Dashboard",
        'iot_devices': [
            {
                "name": "Smart Refrigerator",
                "status": "Connected",
                "details": "Temperature: 3°C, Door: Closed",
                "icon": "❄️"
            },
            {
                "name": "Smart Microwave",
                "status": "Connected",
                "details": "Last Used: 22:30, Mode: Standby",
                "icon": "🍽️"
            },
            {
                "name": "Smart Washing Machine",
                "status": "Offline",
                "details": "Last Cycle: Completed, Ready to Start",
                "icon": "🧺"
            },
            {
                "name": "Smart Dishwasher",
                "status": "Connected",
                "details": "Cycle: Drying, Remaining: 15 min",
                "icon": "🍽️"
            },
            {
                "name": "Smart Oven",
                "status": "Connected",
                "details": "Temperature: 180°C, Mode: Bake",
                "icon": "🥘"
            },
            {
                "name": "Smart Coffee Maker",
                "status": "Offline",
                "details": "Last Brew: Morning, Descaling Needed",
                "icon": "☕"
            }
        ]
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Add styling
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    font-size: 16px;
}
.card {
    font-size: 16px;
}
.device-label {
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# Function to add to activity log
def add_activity(message, entry_type="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.activity_log.insert(0, {"message": message, "time": timestamp, "type": entry_type})
    if len(st.session_state.activity_log) > 10:
        st.session_state.activity_log.pop()

# Simulation functions (toggle_light, update_thermostat, etc. remain the same as in previous implementation)
def toggle_light(room):
    st.session_state.lights[room] = not st.session_state.lights[room]
    status = "on" if st.session_state.lights[room] else "off"
    add_activity(f"{room.capitalize()} light turned {status}", "light")

def update_sensors():
    # Temperature update
    temp_change = (random.random() - 0.5) * 0.8
    st.session_state.temperature = round(st.session_state.temperature + temp_change, 1)

    # Humidity update
    humidity_change = (random.random() - 0.5) * 2
    st.session_state.humidity = min(max(round(st.session_state.humidity + humidity_change), 30), 70)

    # Motion detection
    if random.random() < 0.1:
        st.session_state.motion = not st.session_state.motion
        if st.session_state.motion:
            add_activity("Motion detected", "motion")

    # Temperature alerts
    if st.session_state.temperature > 26 and not any("Temperature above normal" in alert for alert in st.session_state.alerts):
        alert_message = f"Temperature above normal: {st.session_state.temperature}°C"
        st.session_state.alerts.append(alert_message)
        add_activity(alert_message, "alert")

    # Update timestamp
    st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

def main_dashboard():
    # Logout button and title row
    col1, col2, col3 = st.columns([3, 2, 1])
    with col3:
        if st.button("Logout", key="main_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.experimental_rerun()

    # Main title bar
    st.title("🏠 Smart Home Dashboard")
    st.markdown(f"<p style='text-align: right; color: gray; font-size: 0.8rem;'>Last updated: {st.session_state.last_update}</p>", unsafe_allow_html=True)

    # Update data
    update_sensors()

    # Tabs
    tabs = ["Dashboard", "Security", "Energy", "Irrigation", "IoT Devices"]
    cols = st.columns(len(tabs))

    for i, tab in enumerate(tabs):
        if cols[i].button(tab, key=f"tab_{tab}", use_container_width=True):
            st.session_state.current_tab = tab
            st.experimental_rerun()

    # IoT Devices tab
    if st.session_state.current_tab == "IoT Devices":
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🏠 Smart IoT Devices")

        # Refresh devices button
        if st.button("Refresh Devices", key="refresh_iot_devices"):
            for device in st.session_state.iot_devices:
                if random.random() < 0.3:
                    device['status'] = "Connected" if device['status'] == "Offline" else "Offline"
                    
                    # Randomize details
                    if device['name'] == "Smart Refrigerator":
                        device['details'] = f"Temperature: {random.randint(1, 5)}°C, Door: {'Closed' if random.random() > 0.5 else 'Open'}"
                    elif device['name'] == "Smart Microwave":
                        device['details'] = f"Last Used: {random.randint(20, 23)}:{random.randint(0, 59):02d}, Mode: {'Standby' if random.random() > 0.5 else 'Cooking'}"

        # Display devices
        for device in st.session_state.iot_devices:
            status_color = "green" if device["status"] == "Connected" else "red"
            st.markdown(f"""
            <div class='wifi-network'>
                <div>
                    <b>{device['icon']} {device['name']}</b>
                    <span style='color: {status_color}; margin-left: 10px;'>{device['status']}</span>
                    <p style='color: gray; margin: 5px 0;'>{device['details']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

def main():
    # Initialize session state
    initialize_session_state()

    # Check login status
    if not st.session_state.logged_in:
        login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()
