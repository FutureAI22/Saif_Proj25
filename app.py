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
    
    # Update timestamp
    st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

# Main dashboard
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

# Activity Log
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📝 Recent Activity")

if not st.session_state.activity_log:
    st.markdown("<p style='color: gray; font-style: italic;'>No recent activity</p>", unsafe_allow_html=True)
else:
    for entry in st.session_state.activity_log:
        color = {
            "alert": "#f56565",
            "motion": "#48bb78",
            "light": "#ecc94b",
            "thermostat": "#4299e1",
            "fan": "#805ad5",
            "system": "#718096",
            "info": "#a0aec0"
        }.get(entry["type"], "#a0aec0")
        
        st.markdown(
            f"<div class='log-entry' style='border-color: {color};'>{entry['message']} "
            f"<span style='color: gray; font-size: 0.8rem;'>{entry['time']}</span></div>",
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# Auto-refresh the app
st.empty()
time.sleep(3)  # Wait for 3 seconds
st.experimental_rerun()
