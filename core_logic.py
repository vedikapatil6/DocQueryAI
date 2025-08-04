"""
RAG pipeline that:
1. Reads a PDF.
2. Splits it into chunks.
3. Stores the chunks in a Chroma vector DB.
4. Retrieves the most relevant chunks for a user query.
5. Sends context + query to Google Gemini and returns the answer.
"""

import os
import traceback

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

def _join_docs(docs):
    """Concatenate retrieved Document objects into one plain-text context."""
    return "\n\n".join(doc.page_content for doc in docs)

def get_answer_from_pdf(pdf_path: str, query: str) -> str:
    print("🟢  Starting pipeline")

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"   • Loaded {len(documents)} page(s) from {pdf_path}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1_000,
        chunk_overlap=150,
        add_start_index=True,
    )
    chunks = splitter.split_documents(documents)
    print(f"   • Split into {len(chunks)} chunks")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma.from_documents(chunks, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    print("   • Vector store ready")

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",   
        temperature=0.1,
        max_output_tokens=512,
    )
    print("   • Gemini model initialised")

    prompt = PromptTemplate(
        template=(
            "INSTRUCTIONS:\n"
            "You are a helpful assistant. Answer the question based ONLY on the context provided below.\n"
            'If the information is missing, reply: "I don\'t have enough information in the document to answer that."\n'
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
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("   • Generating answer …")
    return chain.invoke(query)

def main():
    pdf_file = "git-cheat-sheet-education.pdf"
    user_query = "What is git?"

    if not os.path.exists(pdf_file):
        print(f"❌  PDF not found: {pdf_file}")
        return

    try:
        answer = get_answer_from_pdf(pdf_file, user_query)
        print("\n🔹 Question:")
        print(user_query)
        print("\n🔹 Answer:")
        print(answer)
    except Exception as exc:
        print("\n❌  An unexpected error occurred.")
        traceback.print_exc()

if __name__ == "__main__":
    main()
