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

# Initialize session state variables if they don't exist
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
# New WiFi related session state variables
if 'wifi_status' not in st.session_state:
    st.session_state.wifi_status = 'connected'  # Options: connected, disconnected
if 'wifi_network' not in st.session_state:
    st.session_state.wifi_network = 'Home_Network_5G'
if 'wifi_signal' not in st.session_state:
    st.session_state.wifi_signal = 85  # Signal strength percentage
if 'available_networks' not in st.session_state:
    st.session_state.available_networks = [
        {'name': 'Home_Network_5G', 'signal': 85, 'security': 'WPA2', 'connected': True},
        {'name': 'Home_Network_2G', 'signal': 92, 'security': 'WPA2', 'connected': False},
        {'name': 'Neighbor_WiFi', 'signal': 62, 'security': 'WPA2', 'connected': False},
        {'name': 'Guest_Network', 'signal': 78, 'security': 'WPA2', 'connected': False},
        {'name': 'IoT_Network', 'signal': 80, 'security': 'WPA2', 'connected': False}
    ]

# Apply custom CSS
st.markdown("""
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
    .wifi-network {
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 5px;
        border: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
    }
    .wifi-signal {
        margin-left: auto;
    }
    .wifi-connected {
        background-color: #e6fffa;
        border-color: #38b2ac;
    }
</style>
""", unsafe_allow_html=True)

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

# New function to connect to WiFi network
def connect_to_wifi(network_name):
    # Disconnect from current network first
    for network in st.session_state.available_networks:
        network['connected'] = False
        
    # Connect to the selected network
    for network in st.session_state.available_networks:
        if network['name'] == network_name:
            network['connected'] = True
            st.session_state.wifi_network = network_name
            st.session_state.wifi_signal = network['signal']
            st.session_state.wifi_status = 'connected'
            add_activity(f"Connected to WiFi network: {network_name}", "wifi")
            break

# New function to refresh WiFi networks
def refresh_wifi_networks():
    # Simulate signal strength changes
    for network in st.session_state.available_networks:
        # Random signal fluctuation between -5 and +5
        network['signal'] = min(max(network['signal'] + random.randint(-5, 5), 20), 99)
    
    add_activity("WiFi networks refreshed", "wifi")

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
    
    # Update WiFi signal strength with small random changes
    if st.session_state.wifi_status == 'connected':
        signal_change = (random.random() - 0.5) * 2
        st.session_state.wifi_signal = min(max(round(st.session_state.wifi_signal + signal_change), 20), 99)
        
        # Small chance of disconnection
        if random.random() < 0.02:
            st.session_state.wifi_status = 'disconnected'
            add_activity("WiFi connection lost", "alert")
    else:
        # Small chance of automatic reconnection
        if random.random() < 0.2:
            st.session_state.wifi_status = 'connected'
            add_activity(f"WiFi reconnected to {st.session_state.wifi_network}", "wifi")
    
    # Update timestamp
    st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

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
tabs = ["Dashboard", "Security", "Energy", "Irrigation", "WiFi"]
cols = st.columns(len(tabs))
for i, tab in enumerate(tabs):
    active_class = "tab-button-active" if st.session_state.current_tab == tab else ""
    if cols[i].button(tab, key=f"tab_{tab}", use_container_width=True):
        st.session_state.current_tab = tab
        st.experimental_rerun()

# Dashboard tab content
if st.session_state.current_tab == "Dashboard":
    # Create two-column layout
    col1, col2 = st.columns(2)

    # Column 1: Sensor Data
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📊 Sensor Data")
        
        # Temperature
        temp_color = "red" if st.session_state.temperature > 25 else "black"
        st.markdown(f"<div class='device-label'>🌡️ Temperature <span class='sensor-value' style='color: {temp_color};'>{st.session_state.temperature}°C</span></div>", unsafe_allow_html=True)
        st.progress((st.session_state.temperature - 15) / 20)  # Scale from 15-35°C
        
        # Humidity
        st.markdown(f"<div class='device-label'>💧 Humidity <span class='sensor-value'>{st.session_state.humidity}%</span></div>", unsafe_allow_html=True)
        st.progress(st.session_state.humidity / 100)
        
        # Motion
        motion_status = "Detected" if st.session_state.motion else "None"
        motion_color = "green" if st.session_state.motion else "gray"
        st.markdown(f"<div class='device-label'>📡 Motion <span class='sensor-value' style='color: {motion_color};'>{motion_status}</span></div>", unsafe_allow_html=True)
        
        # Door statuses
        for door, status in st.session_state.door_status.items():
            door_color = "red" if status == "open" else "green"
            st.markdown(f"<div class='device-label'>🚪 {door.capitalize()} Door <span class='sensor-value' style='color: {door_color};'>{status.capitalize()}</span></div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Column 2: Device Control
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🎮 Device Control")
        
        # Thermostat Control
        st.markdown(f"<div class='device-label'>🌡️ Thermostat <span class='sensor-value'>{st.session_state.thermostat}°C</span></div>", unsafe_allow_html=True)
        new_thermostat = st.slider("", 16, 30, st.session_state.thermostat, key="thermostat_slider", label_visibility="collapsed")
        if new_thermostat != st.session_state.thermostat:
            update_thermostat(new_thermostat)
        
        # Fan Control
        st.markdown("<div class='device-label'>🌀 Fan Speed</div>", unsafe_allow_html=True)
        fan_options = {0: "Off", 1: "Low", 2: "Medium", 3: "High"}
        fan_cols = st.columns(4)
        for i, (level, label) in enumerate(fan_options.items()):
            with fan_cols[i]:
                if st.button(label, key=f"fan_{level}", use_container_width=True):
                    update_fan_speed(level)
        
        # Light Controls
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='device-label'>💡 Lights</div>", unsafe_allow_html=True)
        
        for room in st.session_state.lights:
            status = "On" if st.session_state.lights[room] else "Off"
            status_color = "green" if st.session_state.lights[room] else "gray"
            st.markdown(f"<div class='device-label'>{room.capitalize()} <span style='color: {status_color};'>{status}</span></div>", unsafe_allow_html=True)
            
            light_cols = st.columns([3, 1])
            with light_cols[0]:
                st.markdown(f"<div style='height: 5px;'></div>", unsafe_allow_html=True)
            with light_cols[1]:
                if st.button("Toggle", key=f"light_{room}", use_container_width=True):
                    toggle_light(room)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Security tab content
elif st.session_state.current_tab == "Security":
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🔐 Security System")
        
        # Security system status
        status_color = {
            'disarmed': 'gray',
            'armed_home': 'orange',
            'armed_away': 'green'
        }[st.session_state.security_system]
        
        st.markdown(f"<div class='device-label'>System Status <span class='sensor-value' style='color: {status_color};'>{st.session_state.security_system.replace('_', ' ').capitalize()}</span></div>", unsafe_allow_html=True)
        
        # Security system controls
        security_cols = st.columns(3)
        with security_cols[0]:
            if st.button("Disarm", key="disarm_system", use_container_width=True):
                update_security_system("disarmed")
        with security_cols[1]:
            if st.button("Arm (Home)", key="arm_home", use_container_width=True):
                update_security_system("armed_home")
        with security_cols[2]:
            if st.button("Arm (Away)", key="arm_away", use_container_width=True):
                update_security_system("armed_away")
        
        # Door controls
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='device-label'>🚪 Door Controls</div>", unsafe_allow_html=True)
        
        for door, status in st.session_state.door_status.items():
            door_color = "red" if status == "open" else "green"
            st.markdown(f"<div class='device-label'>{door.capitalize()} <span style='color: {door_color};'>{status.capitalize()}</span></div>", unsafe_allow_html=True)
            
            door_cols = st.columns(2)
            with door_cols[0]:
                if st.button("Open", key=f"open_{door}", use_container_width=True):
                    update_door(door, "open")
            with door_cols[1]:
                if st.button("Close", key=f"close_{door}", use_container_width=True):
                    update_door(door, "closed")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📹 Security Cameras")
        
        # Camera controls
        for camera, status in st.session_state.cameras.items():
            camera_status = "On" if status else "Off"
            camera_color = "green" if status else "gray"
            st.markdown(f"<div class='device-label'>{camera.replace('_', ' ').capitalize()} <span style='color: {camera_color};'>{camera_status}</span></div>", unsafe_allow_html=True)
            
            camera_cols = st.columns([3, 1])
            with camera_cols[0]:
                st.markdown(f"<div style='height: 5px;'></div>", unsafe_allow_html=True)
            with camera_cols[1]:
                if st.button("Toggle", key=f"camera_{camera}", use_container_width=True):
                    toggle_camera(camera)
            
            if status:
                # Placeholder for camera feed (just a gray box in this demo)
                st.markdown(f"<div style='background-color: #d1d1d1; height: 120px; border-radius: 5px; display: flex; justify-content: center; align-items: center;'><p style='color: #555;'>Camera Feed: {camera.replace('_', ' ').capitalize()}</p></div>", unsafe_allow_html=True)
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Energy tab content
elif st.session_state.current_tab == "Energy":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("⚡ Energy Usage")
    
    # Display current energy metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Today's Usage", value=f"{st.session_state.energy_data['daily_usage']:.2f} kWh", delta=f"{(random.random() - 0.6) * 2:.2f} kWh")
    with col2:
        st.metric(label="This Week", value=f"{st.session_state.energy_data['weekly_total']:.2f} kWh", delta=f"{(random.random() - 0.55) * 5:.2f} kWh")
    with col3:
        st.metric(label="This Month", value=f"{st.session_state.energy_data['monthly_total']:.2f} kWh", delta=f"{(random.random() - 0.52) * 10:.2f} kWh")
    
    # Create sample energy data for chart
    energy_times = [f"{i}:00" for i in range(24)]
    energy_values = [random.uniform(0.2, 1.5) for _ in range(24)]
    energy_values[7] = 2.1  # Morning peak
    energy_values[8] = 1.9
    energy_values[18] = 2.3  # Evening peak
    energy_values[19] = 2.5
    energy_values[20] = 2.2
    
    # Create a chart
    st.line_chart(pd.DataFrame({'Energy (kWh)': energy_values}, index=energy_times))
    
    # Energy saving recommendations
    st.subheader("💡 Energy Saving Recommendations")
    recommendations = [
        "Turn off lights in unoccupied rooms",
        "Reduce thermostat by 1°C to save up to 10% on heating costs",
        "Use appliances during off-peak hours (10pm-7am)",
        "Unplug devices not in use to eliminate standby power consumption"
    ]
    
    for i, rec in enumerate(recommendations):
        st.markdown(f"**{i+1}.** {rec}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Irrigation tab content
elif st.session_state.current_tab == "Irrigation":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🌱 Irrigation System")
    
    for zone, data in st.session_state.irrigation_zones.items():
        zone_status = "Active" if data['active'] else "Inactive"
        zone_color = "green" if data['active'] else "gray"
        
        st.markdown(f"<div class='device-label'><b>{zone.replace('_', ' ').capitalize()}</b> <span style='color: {zone_color};'>{zone_status}</span></div>", unsafe_allow_html=True)
        
        zone_cols = st.columns([2, 1, 1])
        with zone_cols[0]:
            st.markdown(f"Schedule: {data['schedule']}, Duration: {data['duration']} min")
        with zone_cols[1]:
            new_schedule = st.time_input(f"New time", label_visibility="collapsed", key=f"time_{zone}")
            new_schedule_str = new_schedule.strftime("%I:%M %p")
        with zone_cols[2]:
            new_duration = st.number_input(f"Duration (min)", min_value=5, max_value=60, value=data['duration'], step=5, label_visibility="collapsed", key=f"duration_{zone}")
        
        control_cols = st.columns([3, 1, 1])
        with control_cols[0]:
            st.markdown(f"<div style='height: 5px;'></div>", unsafe_allow_html=True)
        with control_cols[1]:
            if st.button("Update Schedule", key=f"update_{zone}", use_container_width=True):
                update_irrigation_schedule(zone, new_schedule_str, new_duration)
        with control_cols[2]:
            if st.button("Toggle", key=f"toggle_{zone}", use_container_width=True):
                toggle_irrigation(zone)
        
        st.markdown("<hr>", unsafe_allow_html=True)
    
    # Weather forecast (simplified)
    st.subheader("☁️ Weather Forecast")
    weather_data = [
        {"day": "Today", "icon": "☀️", "temp": "24°C", "precip": "0%"},
        {"day": "Tomorrow", "icon": "⛅", "temp": "22°C", "precip": "10%"},
        {"day": "Day 3", "icon": "🌧️", "temp": "19°C", "precip": "60%"},
    ]
    
    weather_cols = st.columns(len(weather_data))
    for i, day in enumerate(weather_data):
        with weather_cols[i]:
            st.markdown(f"<div style='text-align: center;'><h4>{day['day']}</h4><p style='font-size: 2rem; margin: 0;'>{day['icon']}</p><p>{day['temp']}</p><p>Precipitation: {day['precip']}</p></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# New WiFi tab content
elif st.session_state.current_tab == "WiFi":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📶 WiFi Connection Status")
    
    # WiFi connection status
    status_color = "green" if st.session_state.wifi_status == 'connected' else "red"
    status_text = "Connected" if st.session_state.wifi_status == 'connected' else "Disconnected"
    
    status_cols = st.columns([3, 1])
    with status_cols[0]:
        st.markdown(f"<div class='device-label'>Status <span class='sensor-value' style='color: {status_color};'>{status_text}</span></div>", unsafe_allow_html=True)
    with status_cols[1]:
        if st.button("Refresh", key="refresh_wifi", use_container_width=True):
            refresh_wifi_networks()
            
    # Show current connection details if connected
    if st.session_state.wifi_status == 'connected':
        st.markdown(f"<div class='device-label'>Network <span class='sensor-value'>{st.session_state.wifi_network}</span></div>", unsafe_allow_html=True)
        
        # Display signal strength
        st.markdown(f"<div class='device-label'>Signal Strength <span class='sensor-value'>{st.session_state.wifi_signal}%</span></div>", unsafe_allow_html=True)
        st.progress(st.session_state.wifi_signal / 100)
    
    # Available Networks section
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📡 Available Networks")
    
    # Sort networks by signal strength
    sorted_networks = sorted(st.session_state.available_networks, key=lambda x: x['signal'], reverse=True)
    
    # Replace HTML tags in network names with proper display
    for network in st.session_state.available_networks:
        if '<b>' in network['name'] or '</b>' in network['name']:
            network['name'] = network['name'].replace('<b>', '').replace('</b>', '')
    
    for network in sorted_networks:
        # Determine the CSS class for the network item
        network_class = "wifi-network"
        if network['connected']:
            network_class += " wifi-connected"
            
        # Signal icon based on strength
        if network['signal'] > 80:
            signal_icon = "📶"
        elif network['signal'] > 60:
            signal_icon = "📶"
        elif network['signal'] > 40:
            signal_icon = "📶"
        else:
            signal_icon = "📶"
            
        # Create the network item
        st.markdown(f"<div class='{network_class}'>", unsafe_allow_html=True)
        
        net_cols = st.columns([3, 1])
        with net_cols[0]:
            st.markdown(f"<b>{network['name']}</b> ({network['security']})", unsafe_allow_html=True)
            if network['connected']:
                st.markdown("<span style='color: green; font-size: 0.8rem;'>✓ Connected</span>", unsafe_allow_html=True)
        with net_cols[1]:
            st.markdown(f"<div class='wifi-signal'>{signal_icon} {network['signal']}%</div>", unsafe_allow_html=True)
            
            # Connection button
            if not network['connected']:
                if st.button("Connect", key=f"connect_{network['name']}", use_container_width=True):
                    connect_to_wifi(network['name'])
        
        st.markdown("</div>", unsafe_allow_html=True)
