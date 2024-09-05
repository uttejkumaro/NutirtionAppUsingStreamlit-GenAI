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
    st.set_page_config(page_title="Conversational Image Chatbot")
    st.header("Conversational Image Chatbot")

    # File uploader widget for users to upload an image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

    # Predefined prompt for the chatbot
    image_chatbot_prompt = """
    You are an advanced AI agent capable of combining natural language processing and image recognition technology. 
    Your task is to recognize objects in an image, describe them, and answer questions based on the image content. 
    You utilize a neural encoder-decoder model with a Late Fusion encoder, enabling you to interpret both image and text inputs.

    The basic workflow is:
    1. Given an image (I), a question (Q), and the history of previous questions and answers (H), detect objects in the image.
    2. Generate accurate, meaningful, and grammatically correct responses to the current question based on the detected objects and the conversation history.
    3. Engage in meaningful dialogue about the image, answering follow-up questions based on the visual content.

    Make sure to provide detailed responses when needed, especially when the user asks specific questions about the image or its objects.
    """

    # Text area for users to ask questions about the objects in the image
    user_question = st.text_area("Ask a question about the objects in the image:", key="user_question")

    # Button to analyze the uploaded image
    if st.button("Analyze Image"):
        if uploaded_file is not None:
            try:
                image_data = input_image_setup(uploaded_file)

                # Get the response for the image chatbot prompt
                chatbot_response = get_gemini_response(image_data, image_chatbot_prompt)
                st.session_state.chatbot_response = chatbot_response

                # Get the response for the user's question
                question_response = None
                if user_question:
                    question_response = get_gemini_response(image_data, user_question)
                    st.session_state.question_response = question_response
                else:
                    st.session_state.question_response = None

                # Display the analysis results
                st.subheader("Analysis Results:")
                st.write("Chatbot Analysis:")
                st.write(chatbot_response)
                if question_response:
                    st.write("Answer to your question:")
                    st.write(question_response)

            except FileNotFoundError as e:
                st.error(str(e))
        else:
            st.error("Please upload an image.")

    # Button to save the report
    if st.button("Save Report"):
        if 'chatbot_response' in st.session_state:
            try:
                home_dir = Path.home()
                report_path = home_dir / "image_chatbot_report.txt"
                with open(report_path, "w") as report_file:
                    report_file.write("Chatbot Analysis:\n")
                    report_file.write(st.session_state.chatbot_response + "\n")
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
    st.sidebar.write("1. [Introduction to AI](https://www.coursera.org/courses?query=ai)")
    st.sidebar.write("2. [Basics of NLP](https://www.coursera.org/learn/natural-language-processing)")
    st.sidebar.write("3. [Image Recognition Techniques](https://towardsdatascience.com/an-introduction-to-image-recognition-in-python-324b7da6c3f8)")
