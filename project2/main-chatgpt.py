import streamlit as st
import PyPDF2
import os
import io
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def main():
   st.set_page_config(page_title="AI Resume Critiquer", page_icon= ":)", layout="centered")
   st.title("AI Resume Critiquer")
   st.markdown("Upload your resume in PDF format and get feedback on how to improve it.")
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf","txt"])
   job_role = st.text_input("Enter the job role you are targeting (optional)")
   
   analyze = st.button("Analyze Resume")
   
   if analyze and uploaded_file:
      try:
         file_content = extract_text_from_file(uploaded_file)
         
         if not file_content.strip():
            st.error("The uploaded file is empty or could not be read.")
            st.stop()
            
         prompt = f"""
         You are a helpful assistant that helps users improve their resumes.
         Here is the content of the resume:
         {file_content}
         The user is applying for the following job role:
         {job_role}
         Please provide feedback on how to improve the resume.
         """
         
         client = OpenAI(api_key=OPENAI_API_KEY)
         response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
               {"role": "system", "content": "You are an expert in resume writing and job applications."},
               {"role": "user", "content": prompt}
            ]
         )

         response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
               {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
         )
         st.markdown("### Feedback:")
         st.markdown(response.choices[0].message.content)

      except Exception as e:
         st.error(f"Error: {e}")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text
 
def extract_text_from_file(uploaded_file):
   if uploaded_file.type == "application/pdf":
      return extract_text_from_pdf(io.BytesIO(uploaded_file))
   return uploaded_file.read().decode("utf-8")




if __name__ == "__main__":
    main()
