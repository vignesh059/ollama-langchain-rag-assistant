"""
LangChain tool wrapper for querying uploaded PDF document content via RAG.
"""

from langchain_core.tools import tool
from backend.rag_engine import rag_engine_instance


@tool
def pdf_rag_search_tool(query: str) -> str:
    """
    Use this tool to search for answers, facts, or information from the uploaded PDF document.
    Always use this tool when the user asks a question about the uploaded PDF or document content.
    
    Args:
        query (str): The search query or question related to the uploaded PDF.
    """
    if rag_engine_instance.vectorstore is None:
        return "No PDF document has been uploaded yet. Please upload a PDF file first using the sidebar."

    results = rag_engine_instance.search(query)
    if not results:
        return f"No relevant information found in document '{rag_engine_instance.doc_name}' for query: '{query}'."

    output = f"📄 **PDF Search Results from '{rag_engine_instance.doc_name}'**:\n\n"
    for i, res in enumerate(results, 1):
        output += f"**Chunk {i} (Page {res['page']})**:\n{res['content']}\n\n"

    return output.strip()
