import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app.config import Config


EMBED_MODEL = "text-embedding-3-large"


def load_vectorstore():
    """Load or create FAISS vectorstore for AutoSphere policy documents"""
    vectorstore_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'vectorstore')
    policy_doc_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'autosphere_policy.docx')
    
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL, openai_api_key=Config.OPENAI_API_KEY)
    
    if not os.path.exists(vectorstore_path):
        # Create vectorstore from policy document
        if not os.path.exists(policy_doc_path):
            raise FileNotFoundError(f"Policy document not found: {policy_doc_path}")
        
        loader = Docx2txtLoader(policy_doc_path)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        docs = splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(vectorstore_path)
    else:
        vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
    
    return vectorstore
