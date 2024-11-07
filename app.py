import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import psutil
from pathlib import Path
import matplotlib.pyplot as plt
import time

# Set page config first
st.set_page_config(page_title="Real-Time System Monitor")

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set; if not, display an error message
if not api_key:
    st.error("API key is not set. Please check your .env file.")
else:
    # Configure the generative AI model
    genai.configure(api_key=api_key)

    # Function to get the AI's suggestions for optimizing system performance
    def get_system_suggestions(input_prompt):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_prompt])
        return response.text

    # Monitor system resources using psutil
    def display_system_usage():
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        return cpu_usage, memory_usage, disk_usage

    st.header("Real-Time System Resource Monitor")

    # Sidebar for real-time resource monitoring
    st.sidebar.header("System Resource Usage")

    # AI-generated suggestions based on resource usage
    def update_performance_prompt(cpu_usage, memory_usage, disk_usage):
        return f"""
        The system is currently running with {cpu_usage}% CPU usage, 
        {memory_usage}% memory usage, and {disk_usage}% disk usage.
        Provide suggestions on how to optimize system performance.
        """

    # Checkbox to enable real-time monitoring
    monitoring = st.checkbox("Enable Real-Time Monitoring")

    if monitoring:
        # Update resource usage data
        cpu_usage, memory_usage, disk_usage = display_system_usage()
        st.sidebar.write(f"CPU Usage: {cpu_usage}%")
        st.sidebar.write(f"Memory Usage: {memory_usage}%")
        st.sidebar.write(f"Disk Usage: {disk_usage}%")

        # Button to get AI suggestions for optimizing system performance
        performance_prompt = update_performance_prompt(cpu_usage, memory_usage, disk_usage)
        if st.button("Get AI Suggestions"):
            try:
                suggestions = get_system_suggestions(performance_prompt)
                st.session_state.suggestions = suggestions
                st.subheader("AI-Generated System Performance Suggestions:")
                st.write(suggestions)

            except Exception as e:
                st.error(f"Error generating suggestions: {str(e)}")

        # Real-Time Resource Usage Graph (Track historical data)
        st.subheader("Real-Time Resource Usage Over Time")

        if "history" not in st.session_state:
            st.session_state.history = {
                "cpu": [],
                "memory": [],
                "disk": [],
                "timestamps": []
            }

        # Update historical data for plotting
        st.session_state.history["cpu"].append(cpu_usage)
        st.session_state.history["memory"].append(memory_usage)
        st.session_state.history["disk"].append(disk_usage)
        st.session_state.history["timestamps"].append(time.time())

        # Plot the resource usage over time
        if len(st.session_state.history["timestamps"]) > 1:
            fig, ax = plt.subplots(3, 1, figsize=(10, 6))

            ax[0].plot(st.session_state.history["timestamps"], st.session_state.history["cpu"], label="CPU Usage")
            ax[0].set_title("CPU Usage Over Time")
            ax[0].set_ylabel("CPU (%)")

            ax[1].plot(st.session_state.history["timestamps"], st.session_state.history["memory"], label="Memory Usage", color='orange')
            ax[1].set_title("Memory Usage Over Time")
            ax[1].set_ylabel("Memory (%)")

            ax[2].plot(st.session_state.history["timestamps"], st.session_state.history["disk"], label="Disk Usage", color='green')
            ax[2].set_title("Disk Usage Over Time")
            ax[2].set_ylabel("Disk (%)")
            ax[2].set_xlabel("Time (s)")

            st.pyplot(fig)

        # Set a refresh rate
        time.sleep(2)
        st.experimental_rerun()
