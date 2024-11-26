from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import AsyncGenerator
from fastapi.responses import StreamingResponse
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field
import tempfile
import os
from dotenv import load_dotenv; load_dotenv()

app = FastAPI()

# output schma definition
class QAParser(BaseModel):
    questions: list[str] = Field(..., description="List of all generated MCQ based questions")
    options: list[list[str]]  = Field(..., description="list of all options for the corresponding questions, each containing a list of four options each")
    answers: list[str] = Field(..., description="List of answers corresponding to the set questions, meaning the correct option")
    
template = """You are a professional teacher/lecturer that sets questions for students to practice based on the available class document
The questions should be formatted as follows:
{format_instruction}
<document>
{document}
</document>
"""

parser = PydanticOutputParser(pydantic_object=QAParser)
prompt = PromptTemplate(template=template, input_variables=["document", "format_instruction"])
llm = GoogleGenerativeAI(model="gemini-1.5-flash")

# llm chain to manage qas
chain = prompt.partial(format_instruction=parser.get_format_instructions) | llm | parser



# API routes

@app.get("/")
def home():
    return "Welcome to QA generator, upload a document to /generate_questions/ endpoint to generate questions from it"


@app.post("/generate_questions/")
async def generate_questions(file: UploadFile = File(...)):
    """
    Endpoint to generate MCQs from a multi-page document and stream JSON responses.
    """
    # ensuring file types matchea the required ones
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in ["pdf", "doc", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOC/DOCX files are allowed.")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name
        
    try:
        # load document based on its type
        if file_extension == "pdf":
            loader = PyPDFLoader(temp_file_path)
        elif file_extension in ["doc", "docx"]:
            loader = Docx2txtLoader(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        documents = loader.lazy_load()
        pages = [doc.page_content for doc in documents]
        
        # stream the response
        async def stream_questions() -> AsyncGenerator[str, None]:
            for page_number, page_content in enumerate(pages, start=1):
                try:
                    result = chain.invoke({"document": page_content}).json()
                    yield f'{{"page_number": {page_number}, "qa": {result}}}\n'
                except Exception as e:
                    yield f'{{"page_number": {page_number}, "error": "Failed to process page", "details": "{str(e)}"}}\n'

        
        return StreamingResponse(stream_questions(), media_type="application/json")
    finally:
        os.unlink(temp_file_path)