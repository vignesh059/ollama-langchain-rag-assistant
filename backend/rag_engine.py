"""
RAG Engine for loading PDF documents, text chunking, and FAISS vector indexing.
Includes fallback PDF extractors and empty document checks.
"""

import os
import threading
from typing import List, Optional, Dict, Any

# Suppress TensorFlow GPU/oneDNN warnings and prevent TF conflict with PyTorch
os.environ["USE_TF"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from config import CHUNK_SIZE, CHUNK_OVERLAP, RAG_TOP_K, EMBEDDING_MODEL_NAME


class RAGEngine:
    def __init__(self):
        self.embeddings = None
        self._emb_lock = threading.Lock()
        self.vectorstore: Optional[FAISS] = None
        self.loaded_pdf_path: Optional[str] = None
        self.doc_name: Optional[str] = None
        self.total_pages: int = 0
        self.total_chunks: int = 0

    def _init_embeddings(self):
        """Initializes the embedding model safely with a thread lock."""
        if self.embeddings is None:
            with self._emb_lock:
                if self.embeddings is None:
                    print(f"[INFO] Initializing embedding model: {EMBEDDING_MODEL_NAME}...")
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name=EMBEDDING_MODEL_NAME,
                        encode_kwargs={"normalize_embeddings": True}
                    )
                    print("[INFO] Embedding model initialized successfully.")

    def warmup_embeddings(self):
        """Pre-warms the embedding model in a background thread."""
        try:
            self._init_embeddings()
        except Exception as e:
            print(f"[WARNING] Embedding model warmup failed: {e}")

    def _extract_pdf_docs(self, pdf_path: str) -> List[Document]:
        """
        Attempts to extract PDF pages into LangChain Documents.
        Tries PyPDFLoader first, then falls back to direct pypdf / PyPDF2 readers.
        """
        docs: List[Document] = []
        errors = []

        # 1. Primary: PyPDFLoader
        try:
            loader = PyPDFLoader(pdf_path)
            loaded_docs = loader.load()
            if loaded_docs and any(d.page_content.strip() for d in loaded_docs):
                return loaded_docs
        except Exception as e:
            errors.append(f"PyPDFLoader: {str(e)}")

        # 2. Fallback: pypdf directly
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_path, strict=False)
            extracted_docs = []
            for idx, page in enumerate(reader.pages):
                try:
                    text = page.extract_text() or ""
                    if text.strip():
                        extracted_docs.append(
                            Document(
                                page_content=text,
                                metadata={"source": pdf_path, "page": idx}
                            )
                        )
                except Exception:
                    continue
            if extracted_docs:
                return extracted_docs
        except Exception as e:
            errors.append(f"pypdf reader: {str(e)}")

        # 3. Fallback: PyPDF2
        try:
            import PyPDF2
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                extracted_docs = []
                for idx, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text() or ""
                        if text.strip():
                            extracted_docs.append(
                                Document(
                                    page_content=text,
                                    metadata={"source": pdf_path, "page": idx}
                                )
                            )
                    except Exception:
                        continue
                if extracted_docs:
                    return extracted_docs
        except Exception as e:
            errors.append(f"PyPDF2 reader: {str(e)}")

        if not docs:
            err_details = "; ".join(errors) if errors else "No readable text found"
            raise ValueError(
                f"Could not extract readable text from '{os.path.basename(pdf_path)}'. "
                f"The PDF may be scanned, image-only, or encrypted without text. Details: {err_details}"
            )
        return docs

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Loads a PDF file, splits text into chunks, and builds/updates FAISS vector database.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        # Ensure embeddings are ready
        self._init_embeddings()

        # Load PDF pages with multi-method fallbacks
        docs = self._extract_pdf_docs(pdf_path)
        self.total_pages = len(docs)

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        raw_chunks = text_splitter.split_documents(docs)

        # Filter out empty or whitespace-only chunks
        valid_chunks = [c for c in raw_chunks if c.page_content and c.page_content.strip()]

        if not valid_chunks:
            raise ValueError(
                f"Document '{os.path.basename(pdf_path)}' contains no indexable text chunks. "
                "Please verify that the document contains selectable text and is not an image-only scan."
            )

        self.total_chunks = len(valid_chunks)

        # Index in FAISS
        self.vectorstore = FAISS.from_documents(valid_chunks, self.embeddings)
        self.loaded_pdf_path = pdf_path
        self.doc_name = os.path.basename(pdf_path)

        return {
            "file_name": self.doc_name,
            "total_pages": self.total_pages,
            "total_chunks": self.total_chunks,
            "status": "success"
        }

    def search(self, query: str, top_k: int = RAG_TOP_K) -> List[Dict[str, Any]]:
        """
        Performs similarity search over indexed PDF chunks.
        """
        if self.vectorstore is None:
            return []

        results = self.vectorstore.similarity_search_with_score(query, k=top_k)
        formatted_results = []
        for doc, score in results:
            page = doc.metadata.get("page", 0) + 1  # 1-indexed page
            formatted_results.append({
                "content": doc.page_content,
                "page": page,
                "score": float(score)
            })
        return formatted_results

    def reset(self):
        """
        Clears the vector store and loaded PDF metadata.
        """
        self.vectorstore = None
        self.loaded_pdf_path = None
        self.doc_name = None
        self.total_pages = 0
        self.total_chunks = 0


# Global singleton instance for app-wide RAG access
rag_engine_instance = RAGEngine()

