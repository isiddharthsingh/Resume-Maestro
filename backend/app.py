from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import openai
import fitz  # PyMuPDF for handling PDFs
import traceback
import subprocess
import os

app = FastAPI()

# OpenAI API Key
openai.api_key = "your_open_ai_api_key"  # Securely manage your API key

# Helper function to extract text from a PDF file
def extract_text_from_pdf(pdf_content):
    """Extracts text from a PDF file using PyMuPDF (fitz)."""
    doc = fitz.open("pdf", pdf_content)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to clean LaTeX output from GPT-4
def clean_latex_output(latex_output):
    """Removes any non-LaTeX text from the GPT-4 output."""
    start_index = latex_output.find(r"\documentclass")
    if start_index != -1:
        latex_output = latex_output[start_index:]
    return latex_output

# FastAPI endpoint to generate LaTeX formatted resume and PDF
@app.post("/generate-resume/")
async def generate_resume(job_description: str = Form(...), file: UploadFile = File(...)):
    try:
        # Read the PDF content and extract text
        pdf_content = await file.read()
        resume_text = extract_text_from_pdf(pdf_content)

        # Construct the prompt for GPT-4 to generate a LaTeX formatted resume
        prompt = f"Optimize the following resume based on the provided job description. Use FAANG resume template for resume. Update the technical skills and projects sections as necessary. Do not change or edit the job titles, companies, or dates. Just improve the descriptions under each job title to better fit the job description provided. Also, ensure the descriptions are formatted as bullet points.\n\nResume Text:\n{resume_text}\n\nJob Description:\n{job_description}\n\nCreate a full LaTeX document for the optimized resume and use LaTeX methods and packages to make it fit on just one page."

        # Call OpenAI API to generate the LaTeX content using GPT-4 chat model
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant tasked with creating a LaTeX resume."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000  # Adjust based on the complexity of the resume
        )

        # Fetch the generated LaTeX content
        latex_content = response['choices'][0]['message']['content'].strip()
        latex_content = clean_latex_output(latex_content)

        # Save the generated LaTeX to a file with utf-8 encoding
        latex_file_path = "generated_resume.tex"
        with open(latex_file_path, "w", encoding="utf-8") as f:
            f.write(latex_content)

        # Generate PDF from the LaTeX content using xelatex
        pdf_file_path = generate_pdf(latex_file_path)

        return {
            "message": "Resume generated successfully",
            "latex_content": latex_content,
            "pdf_file_path": pdf_file_path
        }

    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"message": str(e)})

# Function to generate PDF from LaTeX file using xelatex
def generate_pdf(latex_file_path):
    """Generates a PDF file from LaTeX content."""
    # Run xelatex twice to ensure proper table of contents, references, etc.
    subprocess.run(["xelatex", "-interaction=nonstopmode", latex_file_path], check=True)
    subprocess.run(["xelatex", "-interaction=nonstopmode", latex_file_path], check=True)
    pdf_file_path = latex_file_path.replace(".tex", ".pdf")
    if not os.path.exists(pdf_file_path):
        raise FileNotFoundError("PDF generation failed")
    return pdf_file_path

# Endpoint to serve the generated PDF
@app.get("/pdf/{pdf_filename}")
async def get_pdf(pdf_filename: str):
    pdf_path = os.path.join(os.getcwd(), pdf_filename)
    if os.path.exists(pdf_path):
        return FileResponse(path=pdf_path, media_type='application/pdf', filename=pdf_filename)
    else:
        raise HTTPException(status_code=404, detail="PDF not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
