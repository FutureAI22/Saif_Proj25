import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Smart Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Initialize session state variables for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize other session state variables
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Dashboard"

if 'temperature' not in st.session_state:
    st.session_state.temperature = 21.5

if 'humidity' not in st.session_state:
    st.session_state.humidity = 45

if 'lights' not in st.session_state:
    st.session_state.lights = {'living': False, 'kitchen': True, 'bedroom': False}

if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []

# IoT devices for the WiFi tab
if 'iot_devices' not in st.session_state:
    st.session_state.iot_devices = {
        'smart_fridge': {
            'name': 'Smart Fridge',
            'status': 'connected',
            'signal': 95,
        },
        'smart_microwave': {
            'name': 'Smart Microwave',
            'status': 'connected',
            'signal': 88,
        },
        'smart_washing_machine': {
            'name': 'Smart Washing Machine',
            'status': 'connected',
            'signal': 92,
        },
        'smart_tv': {
            'name': 'Smart TV',
            'status': 'connected',
            'signal': 90,
        }
    }

# Apply custom CSS for larger fonts
st.markdown("""
<style>
html, body, [class*="st-"] {
    font-size: 18px !important;
}

h1 {
    font-size: 32px !important;
}

h2 {
    font-size: 28px !important;
}

h3 {
    font-size: 24px !important;
}

.card {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
}

.device-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.7rem;
    font-size: 20px !important;
}

.log-entry {
    border-left: 2px solid blue;
    padding-left: 10px;
    margin-bottom: 5px;
    font-size: 18px !important;
}

.iot-device {
    padding: 15px;
    margin-bottom: 12px;
    border-radius: 5px;
    border: 1px solid #e2e8f0;
    background-color: white;
}

.iot-name {
    font-size: 22px !important;
    font-weight: bold;
    margin-bottom: 10px;
}

.login-container {
    max-width: 500px;
    margin: 0 auto;
    padding: 2rem;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Function to add to activity log
def add_activity(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.activity_log.insert(0, {"message": message, "time": timestamp})
    # Keep only the last 10 entries
    if len(st.session_state.activity_log) > 10:
        st.session_state.activity_log.pop()

# Function to toggle lights
def toggle_light(room):
    st.session_state.lights[room] = not st.session_state.lights[room]
    status = "on" if st.session_state.lights[room] else "off"
    add_activity(f"{room.capitalize()} light turned {status}")

# Function to toggle IoT device status
def toggle_iot_device(device_id):
    current_status = st.session_state.iot_devices[device_id]['status']
    new_status = 'disconnected' if current_status == 'connected' else 'connected'
    st.session_state.iot_devices[device_id]['status'] = new_status
    add_activity(f"{st.session_state.iot_devices[device_id]['name']} {new_status}")

# Main application
if not st.session_state.logged_in:
    # Login page
    st.title("🏠 Smart Home Dashboard")
    
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # For demo, accept any non-empty username/password
        if username and password:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Please enter username and password")
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # Main dashboard after login
    st.title("🏠 Smart Home Dashboard")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
    
    # Simple tab system
    tabs = ["Dashboard", "WiFi"]
    st.write("Select a tab:")
    cols = st.columns(len(tabs))
    
    for i, tab in enumerate(tabs):
        if cols[i].button(tab):
            st.session_state.current_tab = tab
            st.experimental_rerun()
    
    st.write(f"Current tab: {st.session_state.current_tab}")
    
    # Dashboard tab content
    if st.session_state.current_tab == "Dashboard":
        st.header("Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sensor Data")
            st.write(f"Temperature: {st.session_state.temperature}°C")
            st.write(f"Humidity: {st.session_state.humidity}%")
        
        with col2:
            st.subheader("Light Controls")
            for room, status in st.session_state.lights.items():
                st.write(f"{room.capitalize()}: {'On' if status else 'Off'}")
                if st.button(f"Toggle {room}"):
                    toggle_light(room)
    
    # WiFi tab content - simplified version
    elif st.session_state.current_tab == "WiFi":
        st.header("IoT Devices")
        
        for device_id, device in st.session_state.iot_devices.items():
            st.markdown(f"### {device['name']}")
            st.write(f"Status: {device['status'].capitalize()}")
            st.write(f"Signal: {device['signal']}%")
            
            if st.button(f"Toggle {device['name']}"):
                toggle_iot_device(device_id)
            
            st.markdown("---")
    
    # Activity log at the bottom
    st.header("Recent Activity")
    for entry in st.session_state.activity_log:
        st.markdown(f"<div class='log-entry'>{entry['time']} - {entry['message']}</div>", unsafe_allow_html=True)
