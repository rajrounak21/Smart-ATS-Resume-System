import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json
import re
from key import GOOGLE_API_KEY
import os

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)


# Function to get response from Gemini
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(input)
    return response.text  # Ensure response is returned as text


# Function to extract text from uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""  # Prevent NoneType error
    return text


# Function to extract valid JSON from AI response
def extract_json(response):
    match = re.search(r"\{.*\}", response, re.DOTALL)  # Extract JSON block
    if match:
        return match.group(0)  # Return only JSON content
    return None  # If no JSON found, return None


# AI Prompt with strict JSON enforcement
input_prompt = """
Act like an advanced ATS (Application Tracking System) with expertise in software engineering, data science, analytics, and big data. Your job is to analyze the resume against the provided job description.

Provide the response **STRICTLY in JSON FORMAT ONLY**, without any additional text. The output format must be:

{{
  "Job Description Match": "XX%",
  "Missing Keywords": ["keyword1", "keyword2", ...],
  "Profile Summary": "A summary of the resume and its strengths/weaknesses."
}}

Now, analyze the following:
resume: {text}
description: {jd}
"""

# Streamlit UI
st.title("📄 Smart ATS: Resume Checker")
st.text("Optimize Your Resume for ATS Systems")

jd = st.text_area("📌 Paste the Job Description")
uploaded_file = st.file_uploader("📂 Upload Your Resume (PDF)", type="pdf", help="Upload a PDF file")

submit = st.button("🚀 Analyze Resume")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        filled_prompt = input_prompt.format(text=text, jd=jd)
        response = get_gemini_response(filled_prompt)

        try:
            json_response = extract_json(response)  # Extract valid JSON
            if json_response:
                response_dict = json.loads(json_response)  # Convert JSON to dictionary

                st.subheader("✅ Job Description Match:")
                st.text(f"{response_dict['Job Description Match']}")

                st.subheader("🔍 Missing Keywords:")
                st.text(", ".join(response_dict["Missing Keywords"]))

                st.subheader("📌 Profile Summary:")
                profile_summary = response_dict["Profile Summary"].replace(", ", ",\n")
                st.markdown(profile_summary)  # Using markdown for better formatting
            else:
                st.error("⚠️ AI response is not in JSON format. Please try again.")

        except json.JSONDecodeError:
            st.error("⚠️ Could not parse AI response. Please try again.")
    else:
        st.error("⚠️ Please upload a PDF resume.")
