import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import psutil
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

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

    # Log historical data
    historical_data = []

    st.header("Real-Time System Resource Monitor")

    # Sidebar for real-time resource monitoring
    st.sidebar.header("System Resource Usage")
    cpu_usage, memory_usage, disk_usage = display_system_usage()
    st.sidebar.write(f"CPU Usage: {cpu_usage}%")
    st.sidebar.write(f"Memory Usage: {memory_usage}%")
    st.sidebar.write(f"Disk Usage: {disk_usage}%")

    # Log the current usage for historical data
    historical_data.append((cpu_usage, memory_usage, disk_usage))

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

    # Show historical data chart
    if historical_data:
        df = pd.DataFrame(historical_data, columns=['CPU Usage', 'Memory Usage', 'Disk Usage'])
        st.subheader("Historical Resource Usage")
        st.line_chart(df)

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
