import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
import socket
from dataclasses import dataclass
from typing import List, Dict

# Optional import for MQTT
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

import json
import threading

# Constants
DEFAULT_MQTT_BROKER = "broker.hivemq.com"
DEFAULT_MQTT_PORT = 1883

# WiFi Network Management Class
@dataclass
class WifiNetwork:
    ssid: str
    signal_strength: int
    security: str
    connected: bool = False

# Function to update sensors with simulated data
def update_sensors():
    st.session_state.temperature = round(
        max(min(st.session_state.temperature + random.uniform(-0.5, 0.5), 30), 15), 1
    )
    st.session_state.humidity = round(
        max(min(st.session_state.humidity + random.uniform(-2, 2), 100), 20)
    )
    st.session_state.motion = random.random() < 0.1
    st.session_state.energy_data = {
        'daily_usage': round(random.uniform(8, 15), 2),
        'weekly_total': round(random.uniform(50, 90), 2),
        'monthly_total': round(random.uniform(180, 250), 2)
    }
    st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

# Initialize session state variables
def initialize_session_state():
    default_wifi_networks = [
        WifiNetwork("Home_Network", 90, "WPA2", True),
        WifiNetwork("Neighbor_5G", 65, "WPA2"),
        WifiNetwork("GuestNetwork", 45, "WPA"),
        WifiNetwork("IoT_Network", 80, "WPA2"),
        WifiNetwork("CoffeeShop_Free", 25, "Open")
    ]

    default_mqtt_topics = {
        "temperature": "home/sensors/temperature",
        "humidity": "home/sensors/humidity",
        "motion": "home/sensors/motion",
        "lights": "home/lights",
        "thermostat": "home/climate/thermostat",
        "security": "home/security/status",
        "doors": "home/security/doors",
        "irrigation": "home/irrigation"
    }

    default_irrigation_zones = {
        'front_lawn': {'active': False, 'schedule': '06:00 AM', 'duration': 15},
        'backyard': {'active': False, 'schedule': '07:00 AM', 'duration': 20},
        'garden': {'active': False, 'schedule': '05:30 AM', 'duration': 10}
    }

    defaults = {
        'wifi_enabled': True,
        'wifi_connected': True,
        'wifi_ssid': "Home_Network",
        'wifi_password': "********",
        'wifi_ip': "192.168.1.100",
        'wifi_scanning': False,
        'wifi_networks': default_wifi_networks,
        'wifi_connection_history': [
            {"time": (datetime.now() - pd.Timedelta(hours=2)).strftime("%H:%M:%S"), "event": "Connected to Home_Network"},
            {"time": (datetime.now() - pd.Timedelta(minutes=30)).strftime("%H:%M:%S"), "event": "IP Address assigned: 192.168.1.100"}
        ],
        'mqtt_client': None,
        'mqtt_connected': False,
        'mqtt_broker': DEFAULT_MQTT_BROKER,
        'mqtt_port': DEFAULT_MQTT_PORT,
        'mqtt_username': "",
        'mqtt_password': "",
        'mqtt_messages': [],
        'mqtt_topics': default_mqtt_topics,
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
        'irrigation_zones': default_irrigation_zones,
        'current_tab': "Dashboard"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Set page config
st.set_page_config(
    page_title="Smart Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Initialize session state on app start
initialize_session_state()

# Main function to run the app
def main():
    update_sensors()
    time.sleep(3)
    st.experimental_rerun()

# Run the main function
if __name__ == "__main__":
    main()
