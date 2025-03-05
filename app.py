from datetime import datetime
from dataclasses import dataclass

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

# Set page config
st.set_page_config(
    page_title="Smart Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

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
