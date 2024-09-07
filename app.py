import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
from pathlib import Path

# Load environment variables (likely your Google API key)
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set; if not, display an error message
if not api_key:
    st.error("API key is not set. Please check your .env file.")
else:
    # Configure the generative AI model with the provided API key
    genai.configure(api_key=api_key)

    # Function to get the response from the generative AI model
    def get_gemini_response(image_data, input_prompt):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([image_data[0], input_prompt])
        return response.text

    # Function to process the uploaded image
    def input_image_setup(uploaded_file):
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            mime_type = uploaded_file.type
            image_parts = [
                {
                    "mime_type": mime_type,
                    "data": bytes_data
                }
            ]
            return image_parts
        else:
            raise FileNotFoundError("No file uploaded")

    # Set the page configuration for the Streamlit app
    st.set_page_config(page_title="Gemini Health App")
    st.header("Gemini Health App")

    # File uploader widget for users to upload an image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

    # Predefined prompt for calorie calculation
    calorie_prompt = """
    You are an expert nutritionist analyzing the food items in the image. 
    Give detail information of food item. 
    """

    # Text area for users to ask questions about the food in the image
    food_question = st.text_area("Ask a question about the food in the image:", key="food_question")

    # Button to analyze the uploaded image
    if st.button("Analyze Image"):
        if uploaded_file is not None:
            try:
                image_data = input_image_setup(uploaded_file)

                # Get the response for the calorie prompt
                calorie_response = get_gemini_response(image_data, calorie_prompt)
                st.session_state.calorie_response = calorie_response

                # Get the response for the user's question
                question_response = None
                if food_question:
                    question_response = get_gemini_response(image_data, food_question)
                    st.session_state.question_response = question_response
                else:
                    st.session_state.question_response = None

                # Display the analysis results
                st.subheader("Analysis Results:")
                #st.write("Total Calories:")
                st.write(calorie_response)
                if question_response:
                    st.write("Answer to your question:")
                    st.write(question_response)

            except FileNotFoundError as e:
                st.error(str(e))
        else:
            st.error("Please upload an image.")

    # Button to save the report
    if st.button("Save Report"):
        if 'calorie_response' in st.session_state:
            try:
                home_dir = Path.home()
                report_path = home_dir / "nutrition_report.txt"
                with open(report_path, "w") as report_file:
                    report_file.write("Total Calories:\n")
                    report_file.write(st.session_state.calorie_response + "\n")
                    if 'question_response' in st.session_state and st.session_state.question_response:
                        report_file.write("\nAnswer to your question:\n")
                        report_file.write(st.session_state.question_response)

                st.sidebar.write(f"Report saved successfully to {report_path}!")
            except Exception as e:
                st.error(f"Error saving the report: {str(e)}")
        else:
            st.error("Please analyze an image first to generate a report.")

    # Additional sidebar functionalities
    st.sidebar.header("Educational Resources")
    st.sidebar.write("1. [Balanced Diets](https://www.nhs.uk/live-well/eat-well/how-to-eat-a-balanced-diet/eating-a-balanced-diet/)")
    st.sidebar.write("2. [Healthy Eating Tips](https://www.nhs.uk/live-well/eat-well/how-to-eat-a-balanced-diet/eight-tips-for-healthy-eating/)")
    st.sidebar.write("3. [Macronutrients and Micronutrients](https://www.healthline.com/nutrition/micronutrients)")
