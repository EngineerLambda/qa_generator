# QA Generator API

## Overview

The **QA Generator API** is a FastAPI-based service that generates multiple-choice questions (MCQs) from uploaded documents (PDF, DOC, or DOCX). It processes documents page by page, leveraging LangChain and Google Generative AI to create questions. The API streams the responses in JSON format, allowing real-time question generation for each page.

## Features

- Accepts PDF, DOC, and DOCX files as input.
- Generates MCQs, including questions, options, and correct answers, per page.
- Streams results page by page, including the page number in the response.
- Supports lazy loading of large documents to optimise memory usage.
- Handles errors gracefully, returning error details for any failed pages.

## Requirements

### Dependencies
Install the required Python packages:
```bash
pip install fastapi langchain langchain_google_genai langchain_core langchain_community PyPDF2 python-dotenv uvicorn
```

### Environment Variables
Set up the `.env` file in the project root to include your Google Generative AI credentials:
```
GOOGLE_API_KEY=<your_api_key>
```

## Endpoints

### Home
**`GET /`**  
Returns a welcome message and basic usage instructions.

### Generate Questions
**`POST /generate_questions/`**  
Accepts a document file and streams JSON responses for each page.

#### Request
- **File**: PDF, DOC, or DOCX.

#### Response
Each response chunk contains:
- `page_number`: The page being processed.
- `qa`: The generated questions, options, and answers for the page.
- In case of failure, an error message and details.

Example response:
```json
{"page_number": 1, "qa": {"questions": ["What is X?"], "options": [["A", "B", "C", "D"]], "answers": ["A"]}}
```

## Usage

### Run the Server
Start the FastAPI server locally:
```bash
uvicorn app:app --reload
```

### Test the API
Use **Postman**, **cURL**, or similar tools to interact with the API.

#### Example cURL Command:
```bash
curl -X POST "http://127.0.0.1:8000/generate_questions/" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F "file=@example.pdf"
```

### Expected Output
The server streams JSON-formatted responses for each page of the document, allowing you to see the questions as they are generated.

## Project Structure

- **`main.py`**: Core API logic and route definitions.
- **`requirements.txt`**: Python package dependencies.
- **`.env`**: Environment variables for API credentials.

## Notes

- Ensure you have a valid API key for Google Generative AI and configure it in `.env`.
- The API currently supports English-language documents.

---

For questions or contributions, feel free to open an issue or fork this repository!