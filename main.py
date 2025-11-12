import streamlit as st
from groq import Groq
import pdfplumber
from dotenv import load_dotenv
import os

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

def get_file_content(file):
    try :
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        elif file.type == "text/plain":
            return file.read().decode("utf-8")
        else:
            return None
    except Exception as e:
        print(e)
        return None

def create_prompt(resume_content, job_description=None):
    prompt = f"""
                You are an expert resume analyzer.
                User has provided the following resume content:
                {resume_content}
                Please analyze the resume and provide feedback. Limit your response to 500 words.
            """
    if job_description:
        prompt += f"""
                    The user has also provided the following job description:
                    {job_description}
                    Apart from the resume analysis, please also evaluate how well the resume matches the job description.
                """
    return prompt

def start_analysis(resume_file, job_description=None):
    content = get_file_content(resume_file)
    print("-------- Resume Content -------")
    print(content)
    if content is None:
        return "Error reading the file. Please ensure it's a valid document."
    prompt = create_prompt(content, job_description)
    # return "Test"
    try :
        client = Groq(api_key=groq_key)
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None
        )
        print("-------- Analysis Result -------")
        print(response.choices[0].message.content[:500])  # Print first 500 characters of the response
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return "Error during analysis. Please try again later."

def main():
    st.title("Resume Analyzer")

    #Two columns
    col1, col2 = st.columns(2)
    col1.header("Upload Resume")
    uploaded_file = col1.file_uploader("Choose a file", type=["pdf", "txt"])
    upload_jd = col1.checkbox("Also upload Job Description")

    if upload_jd:
        col2.header("Upload Job Description")
        jd = col2.text_area("Paste Job Description here").strip()
    else:
        jd = None
    
    analyze_button = col1.button("Analyze Resume")

    if analyze_button :
        if uploaded_file is not None:
            result = start_analysis(uploaded_file, jd if upload_jd else None)
            st.header("Analysis Result")
            st.write(result)
        else :
            st.warning("Please upload a resume file to analyze.")

if __name__ == "__main__" :
    main()