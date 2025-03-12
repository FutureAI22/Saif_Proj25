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

if 'username' not in st.session_state:
    st.session_state.username = ""

if 'password' not in st.session_state:
    st.session_state.password = ""

# Initialize session state variables
if 'temperature' not in st.session_state:
    st.session_state.temperature = 21.5

if 'humidity' not in st.session_state:
    st.session_state.humidity = 42

if 'motion' not in st.session_state:
    st.session_state.motion = False

if 'lights' not in st.session_state:
    st.session_state.lights = {'living': False, 'kitchen': True, 'bedroom': False}

if 'thermostat' not in st.session_state:
    st.session_state.thermostat = 22

if 'fan_speed' not in st.session_state:
    st.session_state.fan_speed = 0

if 'alerts' not in st.session_state:
    st.session_state.alerts = []

if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []

if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Dashboard"

# IoT devices for WiFi tab
if 'iot_devices' not in st.session_state:
    st.session_state.iot_devices = {
        'smart_fridge': {'name': 'Smart Fridge', 'status': 'connected', 'signal': 95},
        'smart_microwave': {'name': 'Smart Microwave', 'status': 'connected', 'signal': 88},
        'smart_washing_machine': {'name': 'Smart Washing Machine', 'status': 'connected', 'signal': 92},
        'smart_tv': {'name': 'Smart TV', 'status': 'connected', 'signal': 90}
    }

# Apply custom CSS with bigger font
st.markdown("""
<style>
html, body, [class*="st-"] {
    font-size: 18px !important;
}
h1 { font-size: 32px !important; }
h2 { font-size: 28px !important; }
h3 { font-size: 24px !important; }
.card {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
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

# Function to handle login
def login():
    if st.session_state.username == "admin" and st.session_state.password == "password":
        st.session_state.logged_in = True
        return True
    else:
        return False

# Function to add to activity log
def add_activity(message, entry_type="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.activity_log.insert(0, {"message": message, "time": timestamp, "type": entry_type})
    if len(st.session_state.activity_log) > 10:
        st.session_state.activity_log.pop()

# Function to toggle lights
def toggle_light(room):
    st.session_state.lights[room] = not st.session_state.lights[room]
    status = "on" if st.session_state.lights[room] else "off"
    add_activity(f"{room.capitalize()} light turned {status}", "light")

# Function to toggle IoT device
def toggle_iot_device(device_id):
    current_status = st.session_state.iot_devices[device_id]['status']
    new_status = 'disconnected' if current_status == 'connected' else 'connected'
    st.session_state.iot_devices[device_id]['status'] = new_status
    add_activity(f"{st.session_state.iot_devices[device_id]['name']} {new_status}", "iot")

# Login page
if not st.session_state.logged_in:
    st.title("🏠 Smart Home Dashboard")
    
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", key="login_button"):
        st.session_state.username = username
        st.session_state.password = password
        
        if login():
            st.experimental_rerun()
        else:
            st.error("Invalid username or password. Try using admin/password")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main Dashboard (only show if logged in)
else:
    st.title("🏠 Smart Home Dashboard")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
    
    # Tabs
    tabs = ["Dashboard", "WiFi"]
    cols = st.columns(len(tabs))
    
    for i, tab in enumerate(tabs):
        if cols[i].button(tab, key=f"tab_{tab}", use_container_width=True):
            st.session_state.current_tab = tab
            st.experimental_rerun()
    
    # Dashboard tab
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
    
    # WiFi tab with IoT devices
    elif st.session_state.current_tab == "WiFi":
        st.header("IoT Devices")
        
        for device_id, device in st.session_state.iot_devices.items():
            st.subheader(device['name'])
            st.write(f"Status: {device['status'].capitalize()}")
            st.write(f"Signal Strength: {device['signal']}%")
            
            if st.button(f"Toggle {device['name']}"):
                toggle_iot_device(device_id)
            
            st.markdown("---")
    
    # Activity log
    st.header("Recent Activity")
    for entry in st.session_state.activity_log:
        st.write(f"{entry['time']} - {entry['message']}")
