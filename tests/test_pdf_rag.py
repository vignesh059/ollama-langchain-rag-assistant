"""
End-to-end verification for PDF loading, text chunking, FAISS vector indexing, and RAG retrieval.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

from backend.rag_engine import rag_engine_instance
from backend.tools.pdf_rag_tool import pdf_rag_search_tool
from pypdf import PdfWriter


def create_sample_pdf(file_path: str):
    """Creates a basic sample PDF file for RAG verification."""
    writer = PdfWriter()
    # Add a page with plain text content using standard PDF canvas structure
    page = writer.add_blank_page(width=612, height=792)
    
    # We can write a simple PDF file with text content
    writer.write(file_path)


class TestPDFRAG(unittest.TestCase):
    def test_pdf_rag_workflow(self):
        # Create a simple PDF file with plain text or use PyPDF/fpdf if available
        pdf_path = os.path.join(os.path.dirname(__file__), "sample_course_notes.pdf")
        
        # Write standard PDF content manually
        pdf_content = (
            "%PDF-1.4\n"
            "1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
            "2 0 obj <</Type /Pages /Kinds [3 0 R] /Count 1 /Kids [3 0 R]>> endobj\n"
            "3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
            "4 0 obj <</Length 220>> stream\n"
            "BT\n"
            "/F1 12 Tf\n"
            "50 700 Td\n"
            "(Course Title: Advanced Data Structures and Algorithms.) Tj\n"
            "0 -20 Td\n"
            "(Instructor: Dr. Alan Turing. Office: Room 404.) Tj\n"
            "0 -20 Td\n"
            "(Grading Policy: Midterm Exam 40 percent, Final Project 60 percent.) Tj\n"
            "ET\n"
            "endstream\n"
            "endobj\n"
            "5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
            "xreref\n"
            "0 6\n"
            "0000000000 65535 f\n"
            "0000000010 00000 n\n"
            "0000000062 00000 n\n"
            "0000000132 00000 n\n"
            "0000000270 00000 n\n"
            "0000000540 00000 n\n"
            "trailer <</Size 6 /Root 1 0 R>>\n"
            "startxref\n"
            "610\n"
            "%%EOF\n"
        )
        
        with open(pdf_path, "wb") as f:
            f.write(pdf_content.encode("latin1"))

        try:
            # Process PDF
            res = rag_engine_instance.process_pdf(pdf_path)
            self.assertEqual(res["status"], "success")
            self.assertGreaterEqual(res["total_pages"], 1)

            # Query RAG
            rag_output = pdf_rag_search_tool.invoke({"query": "What is the grading policy?"})
            self.assertIn("PDF Search Results", rag_output)
            self.assertIn("Grading Policy", rag_output)
            print("\nRAG Query Output:\n", rag_output)

        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)


if __name__ == "__main__":
    unittest.main()
