import streamlit as st
import requests

st.title("Resume Optimizer")

job_description = st.text_area("Enter Job Description")
resume_file = st.file_uploader("Upload your resume", type=["pdf"])

if st.button("Optimize Resume"):
    if not job_description or not resume_file:
        st.error("Please provide both job description and resume file.")
    else:
        files = {"file": resume_file.getvalue()}
        data = {"job_description": job_description}
        response = requests.post("http://localhost:8000/generate-resume/", data=data, files=files)
        
        if response.status_code == 200:
            result = response.json()
            latex_content = result.get("latex_content", "")
            pdf_file_path = result.get("pdf_file_path", "")
            if latex_content:
                st.success("Resume optimized successfully!")
                st.text_area("Optimized LaTeX Code", latex_content, height=400)
                st.download_button(
                    label="Download LaTeX file",
                    data=latex_content,
                    file_name="optimized_resume.tex",
                    mime="text/plain"
                )
                if pdf_file_path:
                    pdf_response = requests.get(f"http://localhost:8000/pdf/{pdf_file_path.split('/')[-1]}")
                    if pdf_response.status_code == 200:
                        pdf_data = pdf_response.content
                        st.download_button(
                            label="Download PDF file",
                            data=pdf_data,
                            file_name="optimized_resume.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("Failed to fetch the PDF file.")
            else:
                st.error("Failed to generate LaTeX content.")
        else:
            st.error("Failed to generate resume.")
