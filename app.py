import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
from dataclasses import dataclass

# Simplify page configuration
st.set_page_config(page_title="Smart Home Dashboard")

# WiFi Network Management Class
@dataclass
class WifiNetwork:
    ssid: str
    signal_strength: int  # 0-100
    security: str  # WPA, WPA2, WEP, Open
    connected: bool = False

# WiFi-related functions
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

# Function to add to activity log
def add_activity(message, entry_type="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.activity_log.insert(0, {"message": message, "time": timestamp, "type": entry_type})
    # Keep only the last 10 entries
    if len(st.session_state.activity_log) > 10:
        st.session_state.activity_log.pop()

# Function to toggle lights
def toggle_light(room):
    st.session_state.lights[room] = not st.session_state.lights[room]
    status = "on" if st.session_state.lights[room] else "off"
    add_activity(f"{room.capitalize()} light turned {status}", "light")

# Function to change thermostat
def update_thermostat(new_value):
    old_value = st.session_state.thermostat
    st.session_state.thermostat = new_value
    add_activity(f"Thermostat changed from {old_value}°C to {new_value}°C", "thermostat")
    
    # Check if thermostat is set too high
    if new_value > 28 and not any("Thermostat set very high" in alert for alert in st.session_state.alerts):
        st.session_state.alerts.append(f"Thermostat set very high: {new_value}°C")

# Function to change fan speed
def update_fan_speed(new_speed):
    old_speed = st.session_state.fan_speed
    st.session_state.fan_speed = new_speed
    speed_name = "Off" if new_speed == 0 else f"Level {new_speed}"
    old_speed_name = "Off" if old_speed == 0 else f"Level {old_speed}"
    add_activity(f"Fan speed changed from {old_speed_name} to {speed_name}", "fan")

# New function to toggle camera
def toggle_camera(camera):
    st.session_state.cameras[camera] = not st.session_state.cameras[camera]
    status = "on" if st.session_state.cameras[camera] else "off"
    add_activity(f"{camera.replace('_', ' ').capitalize()} camera turned {status}", "security")

# New function to change security system status
def update_security_system(new_status):
    old_status = st.session_state.security_system
    st.session_state.security_system = new_status
    add_activity(f"Security system changed from {old_status} to {new_status}", "security")

# New function to update door status
def update_door(door, status):
    old_status = st.session_state.door_status[door]
    st.session_state.door_status[door] = status
    add_activity(f"{door.capitalize()} door {status}", "security")
    
    # Add alert if door is opened while security system is armed
    if status == "open" and st.session_state.security_system != "disarmed":
        alert_message = f"Security alert: {door} door opened while system armed!"
        st.session_state.alerts.append(alert_message)
        add_activity(alert_message, "alert")

# New function to toggle irrigation zone
def toggle_irrigation(zone):
    st.session_state.irrigation_zones[zone]['active'] = not st.session_state.irrigation_zones[zone]['active']
    status = "activated" if st.session_state.irrigation_zones[zone]['active'] else "deactivated"
    add_activity(f"{zone.replace('_', ' ').capitalize()} irrigation zone {status}", "irrigation")

# New function to update irrigation schedule
def update_irrigation_schedule(zone, schedule, duration):
    st.session_state.irrigation_zones[zone]['schedule'] = schedule
    st.session_state.irrigation_zones[zone]['duration'] = duration
    add_activity(f"{zone.replace('_', ' ').capitalize()} irrigation schedule updated", "irrigation")

# Simulate sensor updates
def update_sensors():
    # Update temperature with small random changes
    temp_change = (random.random() - 0.5) * 0.8
    st.session_state.temperature = round(st.session_state.temperature + temp_change, 1)
    
    # Update humidity with small random changes
    humidity_change = (random.random() - 0.5) * 2
    st.session_state.humidity = min(max(round(st.session_state.humidity + humidity_change), 30), 70)
    
    # Random motion detection (10% chance)
    if random.random() < 0.1:
        if not st.session_state.motion:
            st.session_state.motion = True
            add_activity("Motion detected", "motion")
    else:
        if st.session_state.motion:
            st.session_state.motion = False
    
    # Check for temperature alerts
    if st.session_state.temperature > 26 and not any("Temperature above normal" in alert for alert in st.session_state.alerts):
        alert_message = f"Temperature above normal: {st.session_state.temperature}°C"
        st.session_state.alerts.append(alert_message)
        add_activity(alert_message, "alert")
    
    # Update energy data with small random changes
    energy_change = (random.random() - 0.4) * 0.5
    st.session_state.energy_data['daily_usage'] = round(st.session_state.energy_data['daily_usage'] + energy_change, 2)
    st.session_state.energy_data['weekly_total'] = round(st.session_state.energy_data['weekly_total'] + energy_change * 7, 2)
    st.session_state.energy_data['monthly_total'] = round(st.session_state.energy_data['monthly_total'] + energy_change * 30, 2)
    
    # Update timestamp
    st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

# Initialize session state variables if they don't exist
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
# New session state variables
if 'security_system' not in st.session_state:
    st.session_state.security_system = 'disarmed'  # Options: disarmed, armed_home, armed_away
if 'cameras' not in st.session_state:
    st.session_state.cameras = {'front_door': True, 'backyard': False, 'garage': False}
if 'door_status' not in st.session_state:
    st.session_state.door_status = {'main': 'closed', 'garage': 'closed', 'back': 'closed'}
if 'energy_data' not in st.session_state:
    st.session_state.energy_data = {
        'daily_usage': random.uniform(8, 15),
        'weekly_total': random.uniform(50, 90),
        'monthly_total': random.uniform(180, 250)
    }
if 'irrigation_zones' not in st.session_state:
    st.session_state.irrigation_zones = {
        'front_lawn': {'active': False, 'schedule': '06:00 AM', 'duration': 15},
        'backyard': {'active': False, 'schedule': '07:00 AM', 'duration': 20},
        'garden': {'active': False, 'schedule': '05:30 AM', 'duration': 10}
    }
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Dashboard"

# Custom CSS
custom_css = """
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .alert {
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
        border-left: 4px solid #f56565;
        background-color: #fed7d7;
    }
    .card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .switch {
        position: relative;
        display: inline-block;
        width: 60px;
        height: 34px;
    }
    .device-label {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .log-entry {
        border-left: 2px solid;
        padding-left: 10px;
        margin-bottom: 5px;
        font-size: 0.9rem;
    }
    .sensor-value {
        font-weight: bold;
        float: right;
    }
    .tab-content {
        padding-top: 1rem;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .status-on {
        background-color: #48bb78;
    }
    .status-off {
        background-color: #a0aec0;
    }
    .tab-button {
        padding: 10px 20px;
        margin-right: 5px;
        background-color: #f0f0f0;
        border-radius: 5px 5px 0 0;
        border: none;
        cursor: pointer;
    }
    .tab-button-active {
        background-color: white;
        border-bottom: 2px solid #4299e1;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Main title bar
st.title("🏠 Smart Home Dashboard")
st.markdown(f"<p style='text-align: right; color: gray; font-size: 0.8rem;'>Last updated: {st.session_state.last_update}</p>", unsafe_allow_html=True)

# Update data every 3 seconds
update_sensors()

# Display alerts if any
if st.session_state.alerts:
    for alert in st.session_state.alerts:
        st.markdown(f"<div class='alert'><strong>⚠️ Alert:</strong> {alert}</div>", unsafe_allow_html=True)
    
    # Add clear alerts button
    if st.button("Clear Alerts"):
        st.session_state.alerts = []
        add_activity("All alerts cleared", "system")
        st.experimental_rerun()

# Create tabs using buttons
tabs = ["Dashboard", "Security", "Energy", "Irrigation", "Settings"]
cols = st.columns(len(tabs))
for i, tab in enumerate(tabs):
    active_class = "tab-button-active" if st.session_state.current_tab == tab else ""
    if cols[i].button(tab, key=f"tab_{tab}", use_container_width=True):
        st.session_state.current_tab = tab
        st.experimental_rerun()

# Add WiFi section to Settings tab
if st.session_state.current_tab == "Settings":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📡 WiFi Settings")
    
    # WiFi Connection Status
    wifi_status = "Connected" if st.session_state.wifi_connected else "Disconnected"
    wifi_color = "green" if st.session_state.wifi_connected else "red"
    st.markdown(f"<div class='device-label'>Network Status <span class='sensor-value' style='color: {wifi_color};'>{wifi_status}</span></div>", unsafe_allow_html=True)
    
    if st.session_state.wifi_connected:
        st.markdown(f"<div class='device-label'>Connected Network <span class='sensor-value'>{st.session_state.wifi_ssid}</span></div>", unsafe_allow_html=True)
    
    # Network selection dropdown
    network_ssids = [network.ssid for network in st.session_state.wifi_networks]
    selected_network = st.selectbox("Select Network", network_ssids)
    
    # WiFi connection controls
    col1, col2 = st.columns(2)
    with col1:
        # Connect button
        if st.button("Connect", use_container_width=True):
            connect_to_wifi(selected_network)
            add_activity(f"Attempted to connect to {selected_network}", "wifi")
            st.experimental_rerun()
    
    with col2:
        # Disconnect button
        if st.button("Disconnect", use_container_width=True):
            disconnect_wifi()
            add_activity("Disconnected from WiFi", "wifi")
            st.experimental_rerun()
    
    # Network details
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Available Networks")
    
    for network in st.session_state.wifi_networks:
        # Determine connection and signal status
        connection_status = "Connected" if network.connected else "Not Connected"
        connection_color = "green" if network.connected else "gray"
        
        # Create signal strength visual representation
        signal_width = min(max(network.signal_strength, 10), 100)
        
        st.markdown(f"""
        <div style='display: flex; align-items: center; margin-bottom: 10px;'>
            <div style='width: 200px;'>
                <b>{network.ssid}</b><br>
                <span style='color: {connection_color}; font-size: 0.8rem;'>{connection_status}</span>
            </div>
            <div style='width: 150px; background-color: #e0e0e0; height: 10px; border-radius: 5px; margin-right: 10px;'>
                <div style='width: {signal_width}%; background-color: #48bb78; height: 100%; border-radius: 5px;'></div>
            </div>
            <span>{network.signal_strength}%</span>
            <span style='margin-left: 10px; color: gray; font-size: 0.8rem;'>{network.security}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Scan networks button
    if st.button("Scan Networks"):
        scan_wifi_networks()
        add_activity("Scanning for WiFi networks", "wifi")
        st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
