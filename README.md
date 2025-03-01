# Smart Home Dashboard - Streamlit App

A responsive Smart Home Dashboard built with Streamlit that simulates real-time sensor data and device control.

## Features

- **Real-time sensor data**: Temperature, humidity, and motion detection
- **Device control**: Lights, thermostat, and fan speed
- **Alert system**: Notifications for unusual events
- **Activity log**: Track recent events and changes

## Live Demo

Visit the live app at: [Your Streamlit Cloud URL]

## How to Run Locally

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Deploying to Streamlit Cloud

Follow these steps to deploy this dashboard to Streamlit Cloud:

1. Create a GitHub repository with these files:
   - `app.py` - The main Streamlit application
   - `requirements.txt` - Dependencies
   - `README.md` - This documentation

2. Sign up or log in to [Streamlit Cloud](https://streamlit.io/cloud)

3. Click on "New app" and connect your GitHub repository

4. Configure the app with the following settings:
   - Repository: Your GitHub repository URL
   - Branch: main
   - Main file path: app.py
   - Python version: 3.9 (or higher)

5. Click "Deploy"

## Customization

You can customize this dashboard by:
- Adding more sensors or devices
- Connecting to real IoT devices through APIs
- Implementing user authentication
- Adding historical data visualization

## License

MIT
