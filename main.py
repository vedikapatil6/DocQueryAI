import os
import uuid

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from core_logic import process_and_save_pdf, get_answer_from_doc

PDF_UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="DocQueryAI",
    description="Chat with your PDFs – Semantic RAG Pipeline & FastAPI backend.",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello():
    return {"message": "Hello, DocQueryAI!"}

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        doc_id = str(uuid.uuid4())
        file_path = os.path.join(PDF_UPLOAD_DIR, f"{doc_id}.pdf")
        with open(file_path, "wb") as out_file:
            content = await file.read()
            out_file.write(content)
        num_chunks = process_and_save_pdf(file_path, doc_id)
        return {
            "message": "PDF uploaded and processed successfully.",
            "doc_id": doc_id,
            "chunks": num_chunks
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/query_doc/")
async def query_doc(doc_id: str = Form(...), query: str = Form(...)):
    try:
        answer = get_answer_from_doc(doc_id, query)
        return {"question": query, "answer": answer}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found or not yet processed.")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
