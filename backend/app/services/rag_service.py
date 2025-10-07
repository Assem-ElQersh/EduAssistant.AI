"""
RAG Service Module

This module provides functions and classes for a Retrieval-Augmented Generation (RAG) pipeline
focused on Japanese language teaching. It integrates document parsing, chunking, embedding,
vector storage, and conversational retrieval using LLMs (HuggingFace or Google Gemini).

Sections:
1. Imports and API Key Setup
2. Embedding and LLM Model Initialization
3. Document Parsing and Chunking
4. Vector Store Indexing and Retrieval
5. Syllabus Extraction from HTML
6. RAG Chain Initialization and Querying
7. Chat History Management

Author: [Your Name]
Date: [Current Date]
"""

# ------------------------------
# 1. Imports and API Key Setup
# ------------------------------
import subprocess
import os
import glob
import shutil
from tempfile import TemporaryDirectory
import requests
from bs4 import BeautifulSoup

from huggingface_hub import login
from langchain.vectorstores import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_history_aware_retriever

# Retrieve API keys from environment variables
hf_token = os.environ.get('HF_TOKEN')
google_api = os.environ.get("GOOGLE_API_KEY")
login(hf_token)  # Authenticate with HuggingFace Hub

# ------------------------------
# 2. Embedding and LLM Model Initialization
# ------------------------------

# Set up the embedding model for document chunk vectorization
model_name = "Mohamed-Gamil/multilingual-e5-small-JapaneseTeacher"
embedding_model = HuggingFaceEmbeddings(model_name=model_name)

# Set up the LLM model for conversational generation
# Option 1: HuggingFace model (commented out)
# Option 2: Google Gemini model (active)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0,
    api_key=google_api,
    max_tokens=512,
    transport="rest",
    # Optionally set timeout etc.
)

# ------------------------------
# 3. Document Parsing and Chunking
# ------------------------------

def parse_document(url, output_dir="outputs"):
    """
    Downloads and converts a document from a URL to Markdown format using docling.
    Returns the path to the converted Markdown file.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = None

    os.makedirs("tmp")
    subprocess.run(
        ["docling", "--to", "md", "--pipeline", "vlm", "--vlm-model", "granite_docling", url, "--output", 'tmp'],
        check=True
    )
    md_file = glob.glob(os.path.join('tmp', "*.md"))[0]

    output_path = os.path.join(output_dir, os.path.basename(md_file))
    shutil.move(md_file, output_path)
    shutil.rmtree('tmp/')
    return output_path

def chunk_document(file_path):
    """
    Splits a Markdown document into chunks based on header levels.
    Returns a list of document chunks.
    """
    headers_to_split_on = [
        ("###", "h3"),
        ("####", "h4")
    ]
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    # Read file
    chunks = []
    with open(file_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()
        chunks = md_splitter.split_text(markdown_text)[1:-1]
    return chunks

# ------------------------------
# 4. Vector Store Indexing and Retrieval
# ------------------------------

def index_chunks(persist_dir, chunks, embedding_model):
    """
    Indexes document chunks into a Chroma vector store.
    If the store exists, adds new documents; otherwise, creates a new store.
    Returns the vector database object.
    """
    chroma_exists = os.path.exists(persist_dir)

    if chroma_exists:
        print("🟡 Existing Chroma vector store found — adding new documents...")
        vector_db = Chroma(
            persist_directory=persist_dir,
            embedding_function=embedding_model,
        )
        vector_db.add_documents(chunks)
    else:
        print("🆕 No existing Chroma DB found — creating a new one...")
        docs_ids = [str(i) for i in range(len(chunks))]
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=persist_dir,
            ids=docs_ids,
        )

    # Save / persist to disk
    vector_db.persist()
    print(f"✅ Vector store ready at: {persist_dir}")
    return vector_db

def load_document(url, output_dir, persist_dir, embedding_model):
    """
    Loads a document from a URL, chunks it, indexes it, and returns a retriever object.
    """
    doc = parse_document(url, output_dir)
    chunks = chunk_document(doc)
    vector_db = index_chunks(persist_dir, chunks, embedding_model)
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    return retriever

# ------------------------------
# 5. Syllabus Extraction from HTML (EXAMPLE)
# ------------------------------

def get_syllabus(url):
    """
    Extracts syllabus links from a given HTML page using BeautifulSoup.
    Returns a list of dictionaries with 'title' and 'url' for each lesson.
    """
    response = requests.get(url)
    html = response.text

    # parse with BeautifulSoup
    soup = BeautifulSoup(html, "lxml")

    # find all <a> tags inside <dd>
    links = soup.select("dd a")

    # extract text and href
    data = [{"title": link.get_text(strip=True), "url": link["href"]} for link in links]

    return data

# Example usage: Extract syllabus and index first 40 lessons
syllabus = get_syllabus("https://wasabi-jpn.com/magazine/japanese-grammar/wasabis-online-japanese-grammar-reference/?lang=en")
urls = []
for lesson in syllabus:
    urls.append(lesson['url'])
retriever = None
for i in range(40):
    retriever = load_document(urls[i], '/kaggle/working/syllybus', 'test3', embedding_model)

# ------------------------------
# 6. RAG Chain Initialization and Querying
# ------------------------------

chat_history = [] # should be per session <TEMP>

def init_rag(chat_history):
    """
    Initializes the RAG chain with history-aware retrieval and a Q&A prompt.
    Returns the RAG chain object.
    """
    contextualize_q_system_prompt = """
    Given a chat history and the latest user question
    which might reference context in the chat history,
    formulate a standalone question which can be understood
    without the chat history. Do NOT answer the question,
    just reformulate it if needed and otherwise return it as is.
    """

    contextualize_q_prompt = ChatPromptTemplate(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    user_template = '\n'.join([
        "Answer the next question using the provided context",
        "If the answer is not contained in the context, say 'NO ANSWER IS AVAILABLE'",
        "### Context:",
        "{context}",
        "",
        "### Chat History",
        "{chat_history}",
        "",
        "### Question:",
        "{input}",
        "",
        "### Answer:"
    ])

    qna_prompt = ChatPromptTemplate([
        ("system", "You are a japanese language teacher."),
        ("user", user_template)
    ])

    def format_docs(docs):
        """
        Formats retrieved documents for context presentation.
        """
        return "\n----------\n".join(doc.page_content for doc in docs)

    llm_chain = qna_prompt | llm | StrOutputParser()
    rag_chain = {"context": history_aware_retriever | format_docs, "input": RunnablePassthrough(), 'chat_history': RunnablePassthrough()} | llm_chain
    return rag_chain

def query_rag(session_id, query):
    """
    Queries the RAG chain with a user question and session chat history.
    Returns the model's response.
    """
    # chat_history = get_chat_history(session_id)
    chat_history = []
    model = init_rag(chat_history)
    response = model.invoke({'input':query, 'chat_history': chat_history})
    # update_chat_history(session_id, query, response)
    return response

# ------------------------------
# 7. Chat History Management
# ------------------------------

def update_chat_history(session_id, query, response):
    """
    Updates the chat history for a session with the latest user query and model response.
    """
    # add_row to the table
    chat_history.extend([
        HumanMessage(query),
        AIMessage(response)
    ])