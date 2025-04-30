Certainly! Below is the revised version of the script with the step for **"Collecting PDF Files"** removed, as per your request. The rest of the logic remains intact.

---

# Resume Extraction and Evaluation Logic

This script extracts structured information from PDF resumes, evaluates candidates against predefined criteria, and generates visualizations of candidate scores. Below is a detailed explanation of each component **after removing the "Collecting PDF Files" step**.

---

## **1. Importing Required Libraries**

```python
import google.generativeai as genai
import os
import json
import numpy as np
import random
from copy import deepcopy
import pypdf
import matplotlib.pyplot as plt
import time  # Added for rate limiting
```

- **`google.generativeai`**: Used to interact with the Gemini API for natural language processing (NLP) tasks.
- **`os`**: Handles file and directory operations.
- **`json`**: Parses JSON data for structured outputs.
- **`pypdf`**: Extracts text from PDF files.
- **`matplotlib.pyplot`**: Generates visualizations of candidate scores.
- **`time`**: Introduces delays between API calls to avoid rate-limiting issues.

---

## **2. Configuring the Gemini API**

```python
GOOGLE_API_KEY = "AIzaSyCoGPcEuJifNcE_BqTCZB533P0qizuJ4xk"
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-2.0-flash"
model = genai.GenerativeModel(MODEL_NAME)
```

- **API Key**: Configures the Gemini API with the provided key.
- **Model Name**: Specifies the model (`gemini-2.0-flash`) to use for generating content.
- **GenerativeModel**: Initializes the model instance for making API calls.

---

## **3. Extracting Text from PDFs**

```python
def extract_text_from_pdf(pdf_path):
    """Extracts text content from a PDF file."""
    print(f"Extracting text from PDF: {pdf_path}")
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = "".join(page.extract_text() for page in reader.pages)
        print(f"Successfully extracted text from: {pdf_path}")
        return text
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path}")
        return None
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None
```

- **Purpose**: Reads and extracts text from a given PDF file.
- **Output**: Returns the concatenated text from all pages.
- **Error Handling**: Catches missing files or other errors during extraction.

---

## **4. Extracting Structured Information Using Gemini**

```python
def extract_resume_information(resume_text):
    """Extracts structured information from the resume text using Gemini."""
    print("Calling Gemini API to extract resume information...")
    prompt = f"""
    You are an expert resume parsing assistant. Extract key information from the resume text below and output in JSON format.
    If information isn't explicitly stated, leave the field blank. Return the number of years of experience as a string.
    Estimate experience duration if dates are provided. Include test scores when available.
    Resume text:
    {resume_text}
    Output format:
    {{
        "name": "",
        "email": "",
        "phone_number": "",
        "summary": "",
        "skills": [],
        "number_of_years_experience": "",
        "experience": [{{"title": "", "company": "", "dates": "", "description": ""}}],
        "education": [{{"degree": "", "major": "", "university": "", "graduation_date": ""}}],
        "test_scores": {{"technical_tests": "", "psychometric_tests": ""}},
        "number_of_experiences": 0
    }}
    """
    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip()
        if json_text.startswith("```json"):
            json_text = json_text[7:]  # Remove starting ```json
        if json_text.endswith("```"):
            json_text = json_text[:-3]  # Remove ending ```
        json_text = json_text.strip()  # Clean any extra whitespace
        extracted_data = json.loads(json_text)
        print("Successfully extracted information from Gemini API.")
        return extracted_data
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")
        print(f"Raw Response: {response.text}")
        return None
    except Exception as e:
        print(f"General Error: {e}")
        return None
```

- **Purpose**: Uses Gemini to parse unstructured resume text into structured JSON data.
- **Input**: Raw text extracted from a PDF resume.
- **Output**: JSON object containing fields like name, email, skills, experience, education, etc.
- **Error Handling**: Manages JSON parsing errors and general exceptions.

---

## **5. Evaluating Candidates Against Criteria**

```python
def evaluate_criteria(resume_data, job=None):
    """
    Evaluate candidate against criteria on a scale of 0-5.
    If job is provided, evaluates based on job-specific criteria.
    """
```

### **Criteria Breakdown**
The function evaluates candidates on seven core criteria:

1. **Business Unit Flexibility**:
   - Assesses the diversity of companies and departments worked in.
   - Scores range from `0` (single unit) to `5` (multiple units).

2. **Past Experience**:
   - Estimates total years of experience.
   - Scores range from `0` (<1 year) to `5` (>10 years).

3. **Education Level**:
   - Assigns points based on the highest degree obtained.
   - Scores range from `0` (none) to `5` (PhD or equivalent).

4. **Language Skills**:
   - Checks for fluency in foreign languages.
   - Scores range from `0` (none) to `5` (bilingual/native).

5. **Strategic Thinking**:
   - Looks for keywords related to strategic roles and decisions.
   - Scores range from `0` (none) to `5` (expert).

6. **Communication Skills**:
   - Identifies communication-focused roles and keywords.
   - Scores range from `0` (none) to `5` (expert speaker).

7. **Computer Skills**:
   - Evaluates proficiency in software/tools, prioritizing job-specific requirements.
   - Scores range from `0` (none) to `5` (expert).

### **Final Score Calculation**
- Each criterion is scaled to a 0-100 range.
- A weighted average is calculated to determine the final score.

---

## **6. Processing Resumes in Batches**

```python
def extract(resume_pdfs: list[str]):
    """Extract candidate information from PDFs and return as a list."""
```

- **Purpose**: Processes a batch of PDF resumes, extracts information, and evaluates candidates.
- **Output**: List of candidate data with evaluation scores.

---

## **7. Saving Results to JSON**

```python
def append_to_json(new_data, filename='candidates.json'):
    """Append new data to existing JSON file or create new file."""
```

- **Purpose**: Appends processed candidate data to a JSON file.
- **Sorting**: Ranks candidates by their final score in descending order.

---

## **8. Visualizing Candidate Scores**

```python
def visualize_candidate_scores(filename='candidates.json'):
    """Generate visualization of candidate scores."""
```

- **Purpose**: Creates a bar chart of the top 10 candidates' final scores.
- **Output**: Saves the chart as `candidate_scores.png`.

---

## **9. Processing Applications for a Specific Job**

```python
def process_applications_for_job(job_id, batch_size=3, wait_time=20):
    """
    Process all applications for a specific job, extract data from CVs,
    and save the results to the database.
    """
```

- **Purpose**: Automates the entire pipeline for a specific job ID.
- **Batch Processing**: Processes resumes in batches to avoid API rate limits.
- **Database Integration**: Saves candidate data and rankings to a database.

---

## **Summary**

This script automates the extraction, evaluation, and ranking of candidates from PDF resumes. It leverages NLP models, structured data extraction, and scoring algorithms to provide actionable insights for recruitment processes. The modular design ensures scalability and flexibility for different use cases.

---

Let me know if you need further clarification or modifications!