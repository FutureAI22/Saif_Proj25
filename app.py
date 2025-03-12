import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
import hashlib

# Function to check login credentials
def check_login(username, password):
    # Simple authentication (in a real app, use secure password hashing)
    # Example credentials
    valid_users = {
        "admin": hashlib.md5("password123".encode()).hexdigest()
    }
    
    # Hash the input password
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    return username in valid_users and valid_users[username] == hashed_password

# Login Page
def login_page():
    st.title("🏠 Smart Home Dashboard Login")
    
    # Custom CSS for larger font and centered layout
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
    
    # Login container
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

# Rest of the previous code remains the same, with some modifications to CSS

# Set page config
st.set_page_config(
    page_title="Smart Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Modify the existing CSS to increase font size
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

# Initialize session state variables if they don't exist
# (Previous initialization code remains the same)

# ... (All previous functions like toggle_light, update_thermostat, etc. remain the same)

# Modify the WiFi tab content to show IoT devices
elif st.session_state.current_tab == "WiFi":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🏠 Smart IoT Devices")

    # Define IoT devices with their connection status and additional details
    iot_devices = [
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

    # Display IoT devices
    for device in iot_devices:
        # Determine status color
        status_color = "green" if device["status"] == "Connected" else "red"
        
        # Create device card
        st.markdown(f"""
        <div class='wifi-network'>
            <div>
                <b>{device['icon']} {device['name']}</b>
                <span style='color: {status_color}; margin-left: 10px;'>{device['status']}</span>
                <p style='color: gray; margin: 5px 0;'>{device['details']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Add a refresh button
    if st.button("Refresh Devices", key="refresh_iot_devices"):
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# Main app logic
def main():
    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login_page()
        return

    # Rest of the previous main dashboard code remains the same
    # (All the previous code for dashboard, security, energy, irrigation tabs)

    # Add logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# Run the main app
if __name__ == "__main__":
    main()
