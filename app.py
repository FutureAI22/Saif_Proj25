import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
import socket
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# MQTT Import
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

import json
import threading

# Function to update sensors with simulated data
def update_sensors():
    """Simulate sensor updates for the smart home dashboard"""
    # Update temperature with small random variation
    current_temp = st.session_state.temperature
    temp_change = random.uniform(-0.5, 0.5)
    new_temp = round(max(min(current_temp + temp_change, 30), 15), 1)
    st.session_state.temperature = new_temp

    # Update humidity with small random variation
    current_humidity = st.session_state.humidity
    humidity_change = random.uniform(-2, 2)
    new_humidity = max(min(current_humidity + humidity_change, 100), 20)
    st.session_state.humidity = round(new_humidity)

    # Randomly simulate motion detection
    st.session_state.motion = random.random() < 0.1  # 10% chance of motion

    # Simulate energy data with small variations
    st.session_state.energy_data['daily_usage'] = round(random.uniform(8, 15), 2)
    st.session_state.energy_data['weekly_total'] = round(random.uniform(50, 90), 2)
    st.session_state.energy_data['monthly_total'] = round(random.uniform(180, 250), 2)

    # Update last update timestamp
    st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

# Add activity log function
def add_activity(message, entry_type="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.activity_log.insert(0, {"message": message, "time": timestamp, "type": entry_type})
    # Keep only the last 10 entries
    if len(st.session_state.activity_log) > 10:
        st.session_state.activity_log.pop()

# WiFi Network Management Class
@dataclass
class WifiNetwork:
    ssid: str
    signal_strength: int  # 0-100
    security: str  # WPA, WPA2, WEP, Open
    connected: bool = False

# WiFi-related functions (some placeholders)
def scan_wifi_networks():
    st.session_state.wifi_scanning = True
    time.sleep(2)
    for network in st.session_state.wifi_networks:
        network.signal_strength = max(min(network.signal_strength + random.randint(-5, 5), 100), 5)
    st.session_state.wifi_scanning = False

def connect_to_wifi(ssid, password=""):
    for network in st.session_state.wifi_networks:
        network.connected = False
    
    target_network = next((n for n in st.session_state.wifi_networks if n.ssid == ssid), None)
    if target_network:
        target_network.connected = True
        st.session_state.wifi_connected = True
        st.session_state.wifi_ssid = ssid
        return True
    return False

def disconnect_wifi():
    if st.session_state.wifi_connected:
        for network in st.session_state.wifi_networks:
            network.connected = False
        st.session_state.wifi_connected = False
        return True
    return False

# Initialize session state
def initialize_session_state():
    # WiFi Configuration
    if 'wifi_enabled' not in st.session_state:
        st.session_state.wifi_enabled = True
    if 'wifi_connected' not in st.session_state:
        st.session_state.wifi_connected = True
    if 'wifi_ssid' not in st.session_state:
        st.session_state.wifi_ssid = "Home_Network"
    if 'wifi_networks' not in st.session_state:
        st.session_state.wifi_networks = [
            WifiNetwork("Home_Network", 90, "WPA2", True),
            WifiNetwork("Neighbor_5G", 65, "WPA2"),
            WifiNetwork("GuestNetwork", 45, "WPA"),
            WifiNetwork("IoT_Network", 80, "WPA2"),
            WifiNetwork("CoffeeShop_Free", 25, "Open")
        ]

    # Sensor and device states
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
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
    if 'energy_data' not in st.session_state:
        st.session_state.energy_data = {
            'daily_usage': random.uniform(8, 15),
            'weekly_total': random.uniform(50, 90),
            'monthly_total': random.uniform(180, 250)
        }
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Dashboard"

# Set page configuration
st.set_page_config(page_title="Smart Home Dashboard", page_icon="🏠", layout="wide")

# Initialize session state
initialize_session_state()

# Main dashboard function
def main_dashboard():
    # Title
    st.title("🏠 Smart Home Dashboard")
    
    # Last update time
    st.markdown(f"<p style='text-align: right; color: gray; font-size: 0.8rem;'>Last updated: {st.session_state.last_update}</p>", unsafe_allow_html=True)
    
    # WiFi and MQTT status
    status_cols = st.columns(2)
    with status_cols[0]:
        wifi_status = "🟢 Connected" if st.session_state.wifi_connected else "🔴 Disconnected"
        st.markdown(f"<p style='text-align: right; color: gray; font-size: 0.8rem;'>WiFi Status: {wifi_status} ({st.session_state.wifi_ssid})</p>", unsafe_allow_html=True)
    
    # Sensor Data Section
    st.subheader("📊 Sensor Overview")
    
    cols = st.columns(3)
    with cols[0]:
        st.metric("Temperature", f"{st.session_state.temperature}°C")
    with cols[1]:
        st.metric("Humidity", f"{st.session_state.humidity}%")
    with cols[2]:
        st.metric("Motion", "Detected" if st.session_state.motion else "None")
    
    # Energy Usage Section
    st.subheader("⚡ Energy Usage")
    
    energy_cols = st.columns(3)
    with energy_cols[0]:
        st.metric("Daily Usage", f"{st.session_state.energy_data['daily_usage']} kWh")
    with energy_cols[1]:
        st.metric("Weekly Total", f"{st.session_state.energy_data['weekly_total']} kWh")
    with energy_cols[2]:
        st.metric("Monthly Total", f"{st.session_state.energy_data['monthly_total']} kWh")
    
    # Lights Status
    st.subheader("💡 Lights")
    
    light_cols = st.columns(len(st.session_state.lights))
    for i, (room, status) in enumerate(st.session_state.lights.items()):
        with light_cols[i]:
            st.metric(room.capitalize(), "On" if status else "Off")
    
    # Activity Log
    st.subheader("📝 Recent Activity")
    
    if st.session_state.activity_log:
        for entry in st.session_state.activity_log:
            st.write(f"{entry['time']}: {entry['message']}")
    else:
        st.write("No recent activity")

# Main function to run the app
def main():
    # Render the dashboard
    main_dashboard()
    
    # Update sensors
    update_sensors()
    
    # Add some initial activity if log is empty
    if not st.session_state.activity_log:
        add_activity("Dashboard initialized", "system")
    
    # Schedule next update
    time.sleep(3)
    st.experimental_rerun()

# Run the main function
if __name__ == "__main__":
    main()
