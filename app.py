import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt
import json
import threading
# For WiFi management simulation
import socket
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Set page config
st.set_page_config(
    page_title="Smart Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

# WiFi Network Management Class
@dataclass
class WifiNetwork:
    ssid: str
    signal_strength: int  # 0-100
    security: str  # WPA, WPA2, WEP, Open
    connected: bool = False

# WiFi Configuration
if 'wifi_enabled' not in st.session_state:
    st.session_state.wifi_enabled = True
if 'wifi_connected' not in st.session_state:
    st.session_state.wifi_connected = True
if 'wifi_ssid' not in st.session_state:
    st.session_state.wifi_ssid = "Home_Network"
if 'wifi_password' not in st.session_state:
    st.session_state.wifi_password = "********"
if 'wifi_ip' not in st.session_state:
    st.session_state.wifi_ip = "192.168.1.100"
if 'wifi_scanning' not in st.session_state:
    st.session_state.wifi_scanning = False
if 'wifi_networks' not in st.session_state:
    # Simulated available networks
    st.session_state.wifi_networks = [
        WifiNetwork("Home_Network", 90, "WPA2", True),
        WifiNetwork("Neighbor_5G", 65, "WPA2"),
        WifiNetwork("GuestNetwork", 45, "WPA"),
        WifiNetwork("IoT_Network", 80, "WPA2"),
        WifiNetwork("CoffeeShop_Free", 25, "Open")
    ]
if 'wifi_connection_history' not in st.session_state:
    st.session_state.wifi_connection_history = [
        {"time": (datetime.now() - pd.Timedelta(hours=2)).strftime("%H:%M:%S"), "event": "Connected to Home_Network"},
        {"time": (datetime.now() - pd.Timedelta(minutes=30)).strftime("%H:%M:%S"), "event": "IP Address assigned: 192.168.1.100"}
    ]

# MQTT Configuration
if 'mqtt_client' not in st.session_state:
    st.session_state.mqtt_client = None
if 'mqtt_connected' not in st.session_state:
    st.session_state.mqtt_connected = False
if 'mqtt_broker' not in st.session_state:
    st.session_state.mqtt_broker = "broker.hivemq.com"  # Default public broker
if 'mqtt_port' not in st.session_state:
    st.session_state.mqtt_port = 1883
if 'mqtt_username' not in st.session_state:
    st.session_state.mqtt_username = ""
if 'mqtt_password' not in st.session_state:
    st.session_state.mqtt_password = ""
if 'mqtt_messages' not in st.session_state:
    st.session_state.mqtt_messages = []
if 'mqtt_topics' not in st.session_state:
    st.session_state.mqtt_topics = {
        "temperature": "home/sensors/temperature",
        "humidity": "home/sensors/humidity",
        "motion": "home/sensors/motion",
        "lights": "home/lights",
        "thermostat": "home/climate/thermostat",
        "security": "home/security/status",
        "doors": "home/security/doors",
        "irrigation": "home/irrigation"
    }

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

# MQTT Connection Functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.session_state.mqtt_connected = True
        add_activity("Connected to MQTT broker", "system")
        
        # Subscribe to all topics
        for topic in st.session_state.mqtt_topics.values():
            client.subscribe(f"{topic}/#")
        
        add_activity(f"Subscribed to topics", "system")
    else:
        st.session_state.mqtt_connected = False
        add_activity(f"Failed to connect to MQTT broker, return code: {rc}", "alert")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except:
        payload = msg.payload.decode()
    
    # Add message to log
    st.session_state.mqtt_messages.insert(0, {"topic": topic, "payload": payload, "time": datetime.now().strftime("%H:%M:%S")})
    if len(st.session_state.mqtt_messages) > 20:
        st.session_state.mqtt_messages.pop()
    
    # Process message based on topic
    if topic.startswith(st.session_state.mqtt_topics["temperature"]):
        if isinstance(payload, dict) and "value" in payload:
            st.session_state.temperature = float(payload["value"])
            add_activity(f"Temperature updated from IoT sensor: {payload['value']}°C", "sensor")
    
    elif topic.startswith(st.session_state.mqtt_topics["humidity"]):
        if isinstance(payload, dict) and "value" in payload:
            st.session_state.humidity = float(payload["value"])
            add_activity(f"Humidity updated from IoT sensor: {payload['value']}%", "sensor")
    
    elif topic.startswith(st.session_state.mqtt_topics["motion"]):
        if isinstance(payload, dict) and "detected" in payload:
            motion_detected = bool(payload["detected"])
            if motion_detected and not st.session_state.motion:
                st.session_state.motion = True
                add_activity("Motion detected by IoT sensor", "motion")
            elif not motion_detected and st.session_state.motion:
                st.session_state.motion = False
    
    elif topic.startswith(st.session_state.mqtt_topics["lights"]):
        if isinstance(payload, dict) and "room" in payload and "status" in payload:
            room = payload["room"]
            status = payload["status"]
            if room in st.session_state.lights:
                old_status = st.session_state.lights[room]
                st.session_state.lights[room] = bool(status)
                if old_status != st.session_state.lights[room]:
                    status_str = "on" if st.session_state.lights[room] else "off"
                    add_activity(f"{room.capitalize()} light turned {status_str} via MQTT", "light")
    
    elif topic.startswith(st.session_state.mqtt_topics["doors"]):
        if isinstance(payload, dict) and "door" in payload and "status" in payload:
            door = payload["door"]
            status = payload["status"]
            if door in st.session_state.door_status:
                old_status = st.session_state.door_status[door]
                st.session_state.door_status[door] = status
                if old_status != status:
                    add_activity(f"{door.capitalize()} door {status} via MQTT", "security")

def connect_mqtt():
    # Disconnect if already connected
    if st.session_state.mqtt_client is not None:
        st.session_state.mqtt_client.disconnect()
        st.session_state.mqtt_connected = False
    
    # Create new client
    client_id = f"streamlit-mqtt-{random.randint(0, 1000)}"
    client = mqtt.Client(client_id=client_id)
    
    # Set credentials if provided
    if st.session_state.mqtt_username and st.session_state.mqtt_password:
        client.username_pw_set(st.session_state.mqtt_username, st.session_state.mqtt_password)
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(st.session_state.mqtt_broker, st.session_state.mqtt_port, 60)
        client.loop_start()
        st.session_state.mqtt_client = client
        return True
    except Exception as e:
        add_activity(f"MQTT connection error: {str(e)}", "alert")
        return False

# Function to publish MQTT message
def publish_mqtt(topic, payload):
    if st.session_state.mqtt_connected and st.session_state.mqtt_client is not None:
        try:
            if isinstance(payload, (dict, list)):
                payload_str = json.dumps(payload)
            else:
                payload_str = str(payload)
            
            result = st.session_state.mqtt_client.publish(topic, payload_str)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                add_activity(f"Published to {topic}", "system")
                return True
            else:
                add_activity(f"Failed to publish to {topic}, rc={result.rc}", "alert")
                return False
        except Exception as e:
            add_activity(f"MQTT publish error: {str(e)}", "alert")
            return False
    else:
        add_activity("Cannot publish: MQTT not connected", "alert")
        return False

# Update functions to also send MQTT messages

# Modified function to toggle lights with MQTT
def toggle_light(room):
    st.session_state.lights[room] = not st.session_state.lights[room]
    status = "on" if st.session_state.lights[room] else "off"
    add_activity(f"{room.capitalize()} light turned {status}", "light")
    
    # Publish to MQTT
    topic = f"{st.session_state.mqtt_topics['lights']}/{room}"
    payload = {"room": room, "status": st.session_state.lights[room]}
    publish_mqtt(topic, payload)

# Modified function to change thermostat with MQTT
def update_thermostat(new_value):
    old_value = st.session_state.thermostat
    st.session_state.thermostat = new_value
    add_activity(f"Thermostat changed from {old_value}°C to {new_value}°C", "thermostat")
    
    # Publish to MQTT
    topic = f"{st.session_state.mqtt_topics['thermostat']}/set"
    payload = {"value": new_value, "unit": "celsius"}
    publish_mqtt(topic, payload)
    
    # Check if thermostat is set too high
    if new_value > 28 and not any("Thermostat set very high" in alert for alert in st.session_state.alerts):
        st.session_state.alerts.append(f"Thermostat set very high: {new_value}°C")

# Modified function to update door status with MQTT
def update_door(door, status):
    old_status = st.session_state.door_status[door]
    st.session_state.door_status[door] = status
    add_activity(f"{door.capitalize()} door {status}", "security")
    
    # Publish to MQTT
    topic = f"{st.session_state.mqtt_topics['doors']}/{door}"
    payload = {"door": door, "status": status}
    publish_mqtt(topic, payload)
    
    # Add alert if door is opened while security system is armed
    if status == "open" and st.session_state.security_system != "disarmed":
        alert_message = f"Security alert: {door} door opened while system armed!"
        st.session_state.alerts.append(alert_message)
        add_activity(alert_message, "alert")

# Modified function to update security system with MQTT
def update_security_system(new_status):
    old_status = st.session_state.security_system
    st.session_state.security_system = new_status
    add_activity(f"Security system changed from {old_status} to {new_status}", "security")
    
    # Publish to MQTT
    topic = f"{st.session_state.mqtt_topics['security']}/mode"
    payload = {"mode": new_status}
    publish_mqtt(topic, payload)

# Connect to MQTT if not already connected
if not st.session_state.mqtt_connected:
    connect_mqtt()

# WiFi Functions
def scan_wifi_networks():
    """Simulate scanning for WiFi networks"""
    st.session_state.wifi_scanning = True
    time.sleep(2)  # Simulate scan time
    
    # Update signal strengths with some random variation
    for network in st.session_state.wifi_networks:
        # Add some random fluctuation to signal strength
        signal_change = random.randint(-5, 5)
        network.signal_strength = max(min(network.signal_strength + signal_change, 100), 5)
    
    # Occasionally add or remove a network to simulate dynamic environment
    if random.random() < 0.3:
        if random.random() < 0.5 and len(st.session_state.wifi_networks) > 3:
            # Remove a non-connected network
            non_connected = [n for n in st.session_state.wifi_networks if not n.connected]
            if non_connected:
                st.session_state.wifi_networks.remove(random.choice(non_connected))
        else:
            # Add a new network
            new_ssid = f"Network_{random.randint(1000, 9999)}"
            new_strength = random.randint(20, 85)
            security_types = ["WPA2", "WPA", "Open"]
            new_security = random.choice(security_types)
            st.session_state.wifi_networks.append(WifiNetwork(new_ssid, new_strength, new_security))
    
    st.session_state.wifi_scanning = False
    add_activity("WiFi network scan completed", "system")

def connect_to_wifi(ssid, password=""):
    """Simulate connecting to a WiFi network"""
    # Find the selected network
    target_network = next((n for n in st.session_state.wifi_networks if n.ssid == ssid), None)
    if not target_network:
        add_activity(f"Failed to connect: Network {ssid} not found", "alert")
        return False
    
    # Reset connection status for all networks
    for network in st.session_state.wifi_networks:
        network.connected = False
    
    # Connect to the selected network
    target_network.connected = True
    st.session_state.wifi_connected = True
    st.session_state.wifi_ssid = ssid
    
    # Generate a random IP if connected
    ip_parts = [192, 168, random.randint(0, 1), random.randint(100, 250)]
    st.session_state.wifi_ip = ".".join(map(str, ip_parts))
    
    # Add to connection history
    st.session_state.wifi_connection_history.insert(
        0, 
        {"time": datetime.now().strftime("%H:%M:%S"), "event": f"Connected to {ssid}"}
    )
    st.session_state.wifi_connection_history.insert(
        0, 
        {"time": datetime.now().strftime("%H:%M:%S"), "event": f"IP Address assigned: {st.session_state.wifi_ip}"}
    )
    
    # Keep history limited to recent events
    if len(st.session_state.wifi_connection_history) > 10:
        st.session_state.wifi_connection_history = st.session_state.wifi_connection_history[:10]
    
    add_activity(f"Connected to WiFi network: {ssid}", "system")
    return True

def disconnect_wifi():
    """Disconnect from WiFi"""
    if st.session_state.wifi_connected:
        # Reset connection status for all networks
        for network in st.session_state.wifi_networks:
            network.connected = False
        
        st.session_state.wifi_connected = False
        
        # Add to connection history
        st.session_state.wifi_connection_history.insert(
            0, 
            {"time": datetime.now().strftime("%H:%M:%S"), "event": f"Disconnected from {st.session_state.wifi_ssid}"}
        )
        
        add_activity(f"Disconnected from WiFi network: {st.session_state.wifi_ssid}", "system")
        
        return True
    return False

def toggle_wifi():
    """Toggle WiFi on/off"""
    st.session_state.wifi_enabled = not st.session_state.wifi_enabled
    
    if not st.session_state.wifi_enabled:
        disconnect_wifi()
        add_activity("WiFi turned off", "system")
    else:
        add_activity("WiFi turned on", "system")
        # Don't auto-connect, let user initiate connection

# Main title bar
st.title("🏠 Smart Home Dashboard")
st.markdown(f"<p style='text-align: right; color: gray; font-size: 0.8rem;'>Last updated: {st.session_state.last_update}</p>", unsafe_allow_html=True)

# Display connection statuses
wifi_status = "🟢 Connected" if st.session_state.wifi_connected else "🔴 Disconnected"
wifi_details = f" ({st.session_state.wifi_ssid})" if st.session_state.wifi_connected else ""
mqtt_status = "🟢 Connected" if st.session_state.mqtt_connected else "🔴 Disconnected"

status_cols = st.columns(2)
with status_cols[0]:
    st.markdown(f"<p style='text-align: right; color: gray; font-size: 0.8rem;'>WiFi Status: {wifi_status}{wifi_details}</p>", unsafe_allow_html=True)
with status_cols[1]:
    st.markdown(f"<p style='text-align: right; color: gray; font-size: 0.8rem;'>MQTT Status: {mqtt_status}</p>", unsafe_allow_html=True)

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
tabs = ["Dashboard", "Security", "Energy", "Irrigation", "WiFi", "Settings"]
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

# Settings tab content
# WiFi tab content
elif st.session_state.current_tab == "WiFi":
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📶 WiFi Networks")
        
        # WiFi toggle
        wifi_toggle_cols = st.columns([3, 2])
        with wifi_toggle_cols[0]:
            st.markdown(f"<div class='device-label'>WiFi <span class='sensor-value' style='color: {'green' if st.session_state.wifi_enabled else 'gray'};'>{'Enabled' if st.session_state.wifi_enabled else 'Disabled'}</span></div>", unsafe_allow_html=True)
        with wifi_toggle_cols[1]:
            if st.button("Toggle WiFi", key="toggle_wifi", use_container_width=True):
                toggle_wifi()
                st.experimental_rerun()
        
        if st.session_state.wifi_enabled:
            # Scan button
            scan_col1, scan_col2 = st.columns([3, 1])
            with scan_col2:
                if st.button("Scan Networks", use_container_width=True):
                    scan_wifi_networks()
                    st.experimental_rerun()
            
            # Display networks
            if st.session_state.wifi_scanning:
                st.info("Scanning for networks...")
            else:
                # Sort networks by signal strength
                sorted_networks = sorted(st.session_state.wifi_networks, key=lambda x: (-x.signal_strength))
                
                for i, network in enumerate(sorted_networks):
                    # Display network details
                    signal_icon = "📶" if network.signal_strength > 70 else "📶" if network.signal_strength > 40 else "📶"
                    security_icon = "🔒" if network.security != "Open" else "🔓"
                    
                    network_cols = st.columns([3, 1, 1])
                    with network_cols[0]:
                        st.markdown(f"""
                            <div style="display: flex; align-items: center;">
                                <div style="font-weight: {'bold' if network.connected else 'normal'}; color: {'green' if network.connected else 'black'};">
                                    {network.ssid} {" (Connected)" if network.connected else ""}
                                </div>
                                <div style="margin-left: 10px; color: gray; font-size: 0.8rem;">
                                    {security_icon} {network.security}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with network_cols[1]:
                        # Signal strength bar
                        st.progress(network.signal_strength / 100)
                    
                    with network_cols[2]:
                        if not network.connected:
                            if st.button("Connect", key=f"connect_{i}", use_container_width=True):
                                if network.security != "Open":
                                    # Store the network to connect to after password input
                                    st.session_state.connect_to_ssid = network.ssid
                                else:
                                    # Connect to open network directly
                                    connect_to_wifi(network.ssid)
                                st.experimental_rerun()
                        else:
                            if st.button("Disconnect", key=f"disconnect_{i}", use_container_width=True):
                                disconnect_wifi()
                                st.experimental_rerun()
                    
                    if hasattr(st.session_state, 'connect_to_ssid') and st.session_state.connect_to_ssid == network.ssid:
                        password = st.text_input("Password:", type="password", key=f"pwd_{network.ssid}")
                        pwd_cols = st.columns([2, 1])
                        with pwd_cols[1]:
                            if st.button("Submit", key=f"submit_pwd_{network.ssid}", use_container_width=True):
                                connect_to_wifi(network.ssid, password)
                                delattr(st.session_state, 'connect_to_ssid')
                                st.experimental_rerun()
                    
                    st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
        
        else:
            st.info("WiFi is currently disabled. Enable WiFi to scan for networks.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Current connection details
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📡 Connection Details")
        
        if st.session_state.wifi_connected:
            # Find the connected network
            connected_network = next((n for n in st.session_state.wifi_networks if n.connected), None)
            
            if connected_network:
                st.markdown(f"""
                    <div style='margin-bottom: 15px;'>
                        <div style='font-size: 1.1rem; font-weight: bold;'>{connected_network.ssid}</div>
                        <div>Security: {connected_network.security}</div>
                        <div>Signal Strength: {connected_network.signal_strength}%</div>
                        <div>IP Address: {st.session_state.wifi_ip}</div>
                        <div>MAC Address: AA:BB:CC:DD:EE:FF</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Signal strength indicator
                st.markdown("<div>Signal Strength</div>", unsafe_allow_html=True)
                st.progress(connected_network.signal_strength / 100)
                
                # Disconnect button
                if st.button("Disconnect", use_container_width=True):
                    disconnect_wifi()
                    st.experimental_rerun()
                
                # Refresh IP button
                if st.button("Refresh IP", use_container_width=True):
                    ip_parts = [192, 168, random.randint(0, 1), random.randint(100, 250)]
                    st.session_state.wifi_ip = ".".join(map(str, ip_parts))
                    
                    # Add to connection history
                    st.session_state.wifi_connection_history.insert(
                        0, 
                        {"time": datetime.now().strftime("%H:%M:%S"), "event": f"IP Address refreshed: {st.session_state.wifi_ip}"}
                    )
                    
                    add_activity(f"IP Address refreshed: {st.session_state.wifi_ip}", "system")
                    st.experimental_rerun()
            else:
                st.info("Connection information not available")
        else:
            st.info("Not connected to any WiFi network")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Connection history
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📜 Connection History")
        
        if not st.session_state.wifi_connection_history:
            st.markdown("<p style='color: gray; font-style: italic;'>No connection history</p>", unsafe_allow_html=True)
        else:
            for entry in st.session_state.wifi_connection_history:
                st.markdown(
                    f"<div class='log-entry' style='border-color: #4299e1;'>{entry['event']} "
                    f"<span style='color: gray; font-size: 0.8rem;'>{entry['time']}</span></div>",
                    unsafe_allow_html=True
                )
        
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_tab == "Settings":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("⚙️ System Settings")
    
    # Temperature units
    temp_unit = st.radio("Temperature Units", ["Celsius (°C)", "Fahrenheit (°F)"])
    
    # MQTT Settings
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔌 MQTT Connection Settings")
    
    mqtt_cols = st.columns([2, 1])
    with mqtt_cols[0]:
        new_broker = st.text_input("MQTT Broker", value=st.session_state.mqtt_broker)
        new_port = st.number_input("MQTT Port", min_value=1, max_value=65535, value=st.session_state.mqtt_port)
        new_username = st.text_input("MQTT Username (optional)", value=st.session_state.mqtt_username)
        new_password = st.text_input("MQTT Password (optional)", value=st.session_state.mqtt_password, type="password")
    
    with mqtt_cols[1]:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Connect MQTT", use_container_width=True):
            # Update connection details
            st.session_state.mqtt_broker = new_broker
            st.session_state.mqtt_port = new_port
            st.session_state.mqtt_username = new_username
            st.session_state.mqtt_password = new_password
            
            # Try to connect with new settings
            if connect_mqtt():
                st.success("MQTT connection established!")
            else:
                st.error("Failed to connect to MQTT broker")
    
    # MQTT Topics
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📡 MQTT Topics")
    
    for name, topic in st.session_state.mqtt_topics.items():
        st.text_input(f"{name.capitalize()} Topic", value=topic, key=f"topic_{name}")
    
    if st.button("Save Topics"):
        # Update topics from inputs
        for name in st.session_state.mqtt_topics.keys():
            st.session_state.mqtt_topics[name] = st.session_state[f"topic_{name}"]
        st.success("MQTT topics updated successfully!")
    
    # Notification settings
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📳 Notification Settings")
    
    notification_types = {
        "Security alerts": True,
        "Temperature warnings": True,
        "Motion detection": False,
        "Energy usage reports": True
    }
    
    for alert_type, default in notification_types.items():
        st.checkbox(alert_type, value=default)
    
    # User profiles
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("👤 User Profiles")
    
    profiles = ["Admin", "Family Member", "Guest"]
    selected_profile = st.selectbox("Select profile to edit", profiles)
    
    if selected_profile:
        profile_cols = st.columns(2)
        with profile_cols[0]:
            st.text_input("Name", value=selected_profile)
        with profile_cols[1]:
            st.selectbox("Access Level", ["Full Access", "Limited Access", "Basic Access"])
    
    # Backup and restore
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("💾 Backup & Restore")
    
    backup_cols = st.columns(2)
    with backup_cols[0]:
        if st.button("Backup Configuration", use_container_width=True):
            st.success("Configuration backed up successfully!")
    with backup_cols[1]:
        if st.button("Restore Configuration", use_container_width=True):
            st.info("Select a backup file to restore")
            st.file_uploader("Upload backup file", type=["json"])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # MQTT Message Log
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📩 MQTT Message Log")
    
    if not st.session_state.mqtt_messages:
        st.markdown("<p style='color: gray; font-style: italic;'>No MQTT messages received</p>", unsafe_allow_html=True)
    else:
        for msg in st.session_state.mqtt_messages[:10]:  # Show only the last 10 messages
            st.markdown(
                f"<div class='log-entry' style='border-color: #4299e1;'><b>Topic:</b> {msg['topic']} <br>"
                f"<b>Payload:</b> {str(msg['payload'])} <br>"
                f"<span style='color: gray; font-size: 0.8rem;'>{msg['time']}</span></div>",
                unsafe_allow_html=True
            )
    
    mqtt_cols = st.columns(3)
    with mqtt_cols[0]:
        custom_topic = st.text_input("Topic", placeholder="Enter MQTT topic")
    with mqtt_cols[1]:
        custom_payload = st.text_input("Payload", placeholder="Enter payload")
    with mqtt_cols[2]:
        if st.button("Publish", use_container_width=True):
            if custom_topic and custom_payload:
                if publish_mqtt(custom_topic, custom_payload):
                    st.success(f"Message published to {custom_topic}")
                else:
                    st.error("Failed to publish message")
            else:
                st.error("Topic and payload are required")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Activity Log (shown on all tabs)
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
            "security": "#9f7aea",
            "irrigation": "#38b2ac",
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
