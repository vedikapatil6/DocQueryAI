import os
from typing import List

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

load_dotenv()

VECTORSTORE_DIR = "vectorstores"
if not os.path.exists(VECTORSTORE_DIR):
    os.makedirs(VECTORSTORE_DIR)

def _join_docs(docs: List) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

def process_and_save_pdf(pdf_path: str, doc_id: str) -> int:
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1_000, chunk_overlap=150, add_start_index=True
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=os.path.join(VECTORSTORE_DIR, doc_id),
        collection_name=doc_id
    ).persist()
    return len(chunks)

def get_answer_from_doc(doc_id: str, query: str) -> str:
    vectorstore_path = os.path.join(VECTORSTORE_DIR, doc_id)
    if not os.path.exists(vectorstore_path):
        raise FileNotFoundError(f"No vectorstore for doc_id {doc_id}")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma(
        persist_directory=vectorstore_path,
        embedding_function=embeddings,
        collection_name=doc_id
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.1,
        max_output_tokens=512,
    )

    prompt = PromptTemplate(
        template=(
            "INSTRUCTIONS:\n"
            "You are a helpful assistant. Answer the question based ONLY on the context provided below.\n"
            "If the information is missing, reply: \"I don't have enough information in the document to answer that.\"\n"
            "Do not add extra facts.\n\n"
            "CONTEXT:\n{context}\n\n"
            "QUESTION:\n{question}\n\n"
            "ANSWER:"
        ),
        input_variables=["context", "question"],
    )

    chain = (
        {
            "context": retriever | _join_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain.invoke(query)
