from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {'message' : 'Hello, World!'}


@app.get("/upload_pdf")
def upload_pdf():
    return {'message' : 'Upload PDF'}

@app.get("/query_doc")
def query_doc():
    return {'message' : 'Query Doc'}