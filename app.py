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
    cpu_usage, memory_usage, disk_usage = display_system_usage()
    st.sidebar.write(f"CPU Usage: {cpu_usage}%")
    st.sidebar.write(f"Memory Usage: {memory_usage}%")
    st.sidebar.write(f"Disk Usage: {disk_usage}%")

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
            st.session_state.suggestions = suggestions
            st.subheader("AI-Generated System Performance Suggestions:")
            st.write(suggestions)

        except Exception as e:
            st.error(f"Error generating suggestions: {str(e)}")

    # 1. Real-Time Resource Usage Graph (Track historical data)
    st.subheader("Real-Time Resource Usage Over Time")

    if "history" not in st.session_state:
        st.session_state.history = {
            "cpu": [],
            "memory": [],
            "disk": [],
            "timestamps": []
        }

    if st.button("Start Monitoring"):
        for _ in range(10):  # Monitor for 10 intervals
            cpu, memory, disk = display_system_usage()
            st.session_state.history["cpu"].append(cpu)
            st.session_state.history["memory"].append(memory)
            st.session_state.history["disk"].append(disk)
            st.session_state.history["timestamps"].append(time.time())

            time.sleep(1)

    # Plot the resource usage over time
    if len(st.session_state.history["timestamps"]) > 0:
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

    # 2. Display top 5 processes by CPU and Memory Usage
    st.subheader("Top 5 Processes by CPU and Memory Usage")
    def get_top_processes():
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            processes.append(proc.info)
        sorted_by_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        sorted_by_memory = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]
        return sorted_by_cpu, sorted_by_memory

    top_cpu_processes, top_memory_processes = get_top_processes()

    st.write("Top 5 Processes by CPU Usage:")
    for proc in top_cpu_processes:
        st.write(f"Process {proc['name']} (PID {proc['pid']}): {proc['cpu_percent']}% CPU")

    st.write("Top 5 Processes by Memory Usage:")
    for proc in top_memory_processes:
        st.write(f"Process {proc['name']} (PID {proc['pid']}): {proc['memory_percent']}% Memory")

    # 3. Alert when CPU or Memory crosses threshold
    st.subheader("Set Alerts for Resource Usage Thresholds")

    cpu_threshold = st.number_input("Set CPU Threshold (%)", min_value=0, max_value=100, value=80)
    memory_threshold = st.number_input("Set Memory Threshold (%)", min_value=0, max_value=100, value=80)

    if cpu_usage > cpu_threshold:
        st.error(f"CPU usage has exceeded {cpu_threshold}%!")
    if memory_usage > memory_threshold:
        st.error(f"Memory usage has exceeded {memory_threshold}%!")

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
