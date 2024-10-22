import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import psutil
import time
import matplotlib.pyplot as plt
import pandas as pd

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set; if not, display an error message
if not api_key:
    st.error("API key is not set. Please check your .env file.")
else:
    # Configure the generative AI model
    genai.configure(api_key=api_key)

    # Function to get AI's suggestions for optimizing system performance
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

    # Track system resource usage history for plotting
    usage_history = {'cpu': [], 'memory': [], 'disk': []}

    # Set up threshold monitoring
    cpu_threshold = st.sidebar.slider("Set CPU Usage Threshold (%)", 0, 100, 80)
    memory_threshold = st.sidebar.slider("Set Memory Usage Threshold (%)", 0, 100, 80)
    disk_threshold = st.sidebar.slider("Set Disk Usage Threshold (%)", 0, 100, 90)

    st.set_page_config(page_title="Real-Time System Monitor")
    st.header("Real-Time System Resource Monitor")

    # Sidebar for real-time resource monitoring
    st.sidebar.header("System Resource Usage")
    cpu_usage, memory_usage, disk_usage = display_system_usage()
    st.sidebar.write(f"CPU Usage: {cpu_usage}%")
    st.sidebar.write(f"Memory Usage: {memory_usage}%")
    st.sidebar.write(f"Disk Usage: {disk_usage}%")

    # Save usage history for visualization
    usage_history['cpu'].append(cpu_usage)
    usage_history['memory'].append(memory_usage)
    usage_history['disk'].append(disk_usage)

    # Alert the user if any usage exceeds the threshold
    if cpu_usage > cpu_threshold:
        st.warning(f"⚠️ CPU usage is above {cpu_threshold}%: {cpu_usage}%")
    if memory_usage > memory_threshold:
        st.warning(f"⚠️ Memory usage is above {memory_threshold}%: {memory_usage}%")
    if disk_usage > disk_threshold:
        st.warning(f"⚠️ Disk usage is above {disk_threshold}%: {disk_usage}%")

    # AI-generated suggestions based on resource usage
    performance_prompt = f"""
    The system is currently running with {cpu_usage}% CPU usage, 
    {memory_usage}% memory usage, and {disk_usage}% disk usage.
    Provide suggestions on how to optimize system performance.
    """

    # Button to get AI suggestions for optimizing system performance
    if st.button("Get AI Suggestions"):
        try:
            suggestions = get_system_suggestions(performance_prompt)
            if 'suggestions_history' not in st.session_state:
                st.session_state.suggestions_history = []
            st.session_state.suggestions = suggestions
            st.session_state.suggestions_history.append(suggestions)
            st.subheader("AI-Generated System Performance Suggestions:")
            st.write(suggestions)

        except Exception as e:
            st.error(f"Error generating suggestions: {str(e)}")

    # Display the history of AI suggestions
    if 'suggestions_history' in st.session_state:
        st.subheader("History of AI Suggestions:")
        for i, suggestion in enumerate(st.session_state.suggestions_history):
            st.write(f"Suggestion {i+1}:")
            st.write(suggestion)

    # Plot CPU, Memory, and Disk usage over time
    st.subheader("Resource Usage Over Time")
    fig, ax = plt.subplots()
    df = pd.DataFrame(usage_history)
    df.plot(ax=ax)
    st.pyplot(fig)

    # List top processes by CPU and memory usage
    st.subheader("Top Resource-Consuming Processes")
    top_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        top_processes.append(proc.info)

    top_processes = sorted(top_processes, key=lambda p: p['cpu_percent'], reverse=True)[:5]
    for i, proc in enumerate(top_processes, 1):
        st.write(f"{i}. {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}%, Memory: {proc['memory_percent']}%")

    # Button to save the report
    if st.button("Save Report"):
        if 'suggestions' in st.session_state:
            try:
                home_dir = Path.home()
                report_path = home_dir / "system_performance_report.txt"
                with open(report_path, "w") as report_file:
                    report_file.write("System Resource Usage:\n")
                    report_file.write(f"CPU Usage: {cpu_usage}%\n")
                    report_file.write(f"Memory Usage: {memory_usage}%\n")
                    report_file.write(f"Disk Usage: {disk_usage}%\n")
                    report_file.write("\nAI Suggestions:\n")
                    report_file.write(st.session_state.suggestions)

                st.sidebar.write(f"Report saved successfully to {report_path}!")
            except Exception as e:
                st.error(f"Error saving the report: {str(e)}")
        else:
            st.error("Please generate AI suggestions first.")

