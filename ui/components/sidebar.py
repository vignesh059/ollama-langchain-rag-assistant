"""
Sidebar Component for App Controls, PDF Upload, Ollama Model Selector, and Memory Management.
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Callable, Optional

from ui.styles import THEME, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_SMALL, FONT_BOLD
from backend.llm_engine import llm_engine_instance
from backend.rag_engine import rag_engine_instance
from backend.memory_engine import memory_engine_instance
from config import DEFAULT_MODEL, AVAILABLE_MODELS



class Sidebar(ctk.CTkFrame):
    def __init__(
        self, 
        master, 
        on_pdf_loaded_callback: Optional[Callable[[str], None]] = None,
        on_memory_cleared_callback: Optional[Callable[[], None]] = None,
        on_model_changed_callback: Optional[Callable[[str], None]] = None
    ):
        super().__init__(
            master, 
            fg_color=THEME["bg_sidebar"], 
            width=280,
            corner_radius=0
        )
        self.pack_propagate(False)

        self.on_pdf_loaded = on_pdf_loaded_callback
        self.on_memory_cleared = on_memory_cleared_callback
        self.on_model_changed = on_model_changed_callback

        self.selected_model = ctk.StringVar(value=DEFAULT_MODEL)

        self._build_ui()
        self.refresh_ollama_status()

    def _build_ui(self):
        # App Header
        header = ctk.CTkLabel(
            self, 
            text="🤖 Ollama Chatbot", 
            font=FONT_TITLE, 
            text_color=THEME["accent_cyan"]
        )
        header.pack(padx=16, pady=(20, 4), anchor="w")

        subtitle = ctk.CTkLabel(
            self,
            text="LangChain • RAG • Tools • Memory",
            font=FONT_SMALL,
            text_color=THEME["text_muted"]
        )
        subtitle.pack(padx=16, pady=(0, 16), anchor="w")

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=THEME["border_color"]).pack(fill="x", padx=16, pady=4)

        # 1. Ollama Connection & Model Section
        ollama_title = ctk.CTkLabel(
            self, 
            text="Ollama Engine Status", 
            font=FONT_SUBTITLE, 
            text_color=THEME["text_primary"]
        )
        ollama_title.pack(padx=16, pady=(12, 4), anchor="w")

        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(padx=16, pady=4, fill="x")

        self.status_dot = ctk.CTkLabel(
            self.status_frame, 
            text="●", 
            font=("Segoe UI", 16), 
            text_color=THEME["status_disconnected"]
        )
        self.status_dot.pack(side="left", padx=(0, 6))

        self.status_text = ctk.CTkLabel(
            self.status_frame, 
            text="Checking server...", 
            font=FONT_SMALL, 
            text_color=THEME["text_secondary"]
        )
        self.status_text.pack(side="left")

        # Model Selector
        model_label = ctk.CTkLabel(self, text="Select Llama Model:", font=FONT_SMALL, text_color=THEME["text_muted"])
        model_label.pack(padx=16, pady=(8, 2), anchor="w")

        self.model_dropdown = ctk.CTkOptionMenu(
            self,
            values=AVAILABLE_MODELS,
            variable=self.selected_model,
            fg_color=THEME["bg_main"],
            button_color=THEME["accent_cyan"],
            button_hover_color=THEME["accent_violet"],
            dropdown_fg_color=THEME["bg_card"],
            command=self._on_model_select
        )
        self.model_dropdown.pack(padx=16, pady=(0, 8), fill="x")

        # Refresh status button
        refresh_btn = ctk.CTkButton(
            self,
            text="🔄 Refresh Ollama Status",
            font=FONT_SMALL,
            fg_color=THEME["bg_main"],
            hover_color=THEME["border_color"],
            command=self.refresh_ollama_status
        )
        refresh_btn.pack(padx=16, pady=(0, 12), fill="x")

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=THEME["border_color"]).pack(fill="x", padx=16, pady=4)

        # 2. PDF RAG Document Section
        pdf_title = ctk.CTkLabel(self, text="📄 RAG PDF Upload", font=FONT_SUBTITLE, text_color=THEME["text_primary"])
        pdf_title.pack(padx=16, pady=(12, 4), anchor="w")

        self.upload_btn = ctk.CTkButton(
            self,
            text="📤 Upload & Index PDF",
            font=FONT_BOLD,
            fg_color=THEME["accent_cyan"],
            hover_color=THEME["accent_violet"],
            text_color="#000000",
            command=self._on_upload_pdf_clicked
        )
        self.upload_btn.pack(padx=16, pady=4, fill="x")

        # PDF Info Card
        self.pdf_card = ctk.CTkFrame(self, fg_color=THEME["bg_main"], corner_radius=8)
        self.pdf_card.pack(padx=16, pady=8, fill="x")

        self.pdf_name_lbl = ctk.CTkLabel(
            self.pdf_card,
            text="No PDF Loaded",
            font=FONT_BOLD,
            text_color=THEME["text_muted"],
            wraplength=220
        )
        self.pdf_name_lbl.pack(padx=10, pady=(8, 2), anchor="w")

        self.pdf_details_lbl = ctk.CTkLabel(
            self.pdf_card,
            text="Upload a PDF document to query with RAG.",
            font=FONT_SMALL,
            text_color=THEME["text_muted"],
            wraplength=220,
            justify="left"
        )
        self.pdf_details_lbl.pack(padx=10, pady=(0, 8), anchor="w")

        self.reset_pdf_btn = ctk.CTkButton(
            self,
            text="🗑️ Clear PDF Index",
            font=FONT_SMALL,
            fg_color=THEME["bg_main"],
            hover_color="#991B1B",
            text_color=THEME["text_muted"],
            command=self._on_reset_pdf_clicked
        )
        self.reset_pdf_btn.pack(padx=16, pady=(0, 12), fill="x")

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=THEME["border_color"]).pack(fill="x", padx=16, pady=4)

        # 3. Active Tools Card
        tools_title = ctk.CTkLabel(self, text="🛠️ Integrated Tools", font=FONT_SUBTITLE, text_color=THEME["text_primary"])
        tools_title.pack(padx=16, pady=(12, 4), anchor="w")

        tools_box = ctk.CTkFrame(self, fg_color=THEME["bg_main"], corner_radius=8)
        tools_box.pack(padx=16, pady=4, fill="x")

        t1 = ctk.CTkLabel(tools_box, text="• 🌐 Wikipedia Search Tool", font=FONT_SMALL, text_color=THEME["tool_wiki_bg"])
        t1.pack(padx=10, pady=(6, 2), anchor="w")

        t2 = ctk.CTkLabel(tools_box, text="• 📊 Custom Attendance Tool", font=FONT_SMALL, text_color=THEME["tool_att_bg"])
        t2.pack(padx=10, pady=2, anchor="w")

        t3 = ctk.CTkLabel(tools_box, text="• 📄 PDF RAG Search Tool", font=FONT_SMALL, text_color=THEME["tool_pdf_bg"])
        t3.pack(padx=10, pady=(2, 6), anchor="w")

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=THEME["border_color"]).pack(fill="x", padx=16, pady=4)

        # 4. Memory Control Section
        memory_title = ctk.CTkLabel(self, text="🧠 Conversation Memory", font=FONT_SUBTITLE, text_color=THEME["text_primary"])
        memory_title.pack(padx=16, pady=(12, 4), anchor="w")

        clear_mem_btn = ctk.CTkButton(
            self,
            text="🧹 Clear Chat Memory",
            font=FONT_BOLD,
            fg_color="#991B1B",
            hover_color="#7F1D1D",
            command=self._on_clear_memory_clicked
        )
        clear_mem_btn.pack(padx=16, pady=(4, 16), fill="x")

    def refresh_ollama_status(self):
        """Checks connection to Ollama and updates status dot & dropdown."""
        is_online, msg, available_models = llm_engine_instance.check_connection()
        if is_online:
            self.status_dot.configure(text_color=THEME["status_connected"])
            self.status_text.configure(text="Connected to Ollama", text_color=THEME["status_connected"])
            if available_models:
                self.model_dropdown.configure(values=available_models)
        else:
            self.status_dot.configure(text_color=THEME["status_disconnected"])
            self.status_text.configure(text=msg, text_color=THEME["status_disconnected"])

    def _on_model_select(self, model_name: str):
        if self.on_model_changed:
            self.on_model_changed(model_name)

    def _on_upload_pdf_clicked(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF File for RAG",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not file_path:
            return

        self.upload_btn.configure(state="disabled", text="⏳ Indexing PDF...")
        self.pdf_name_lbl.configure(text=f"📄 Loading {os.path.basename(file_path)}...", text_color=THEME["text_muted"])
        self.pdf_details_lbl.configure(text="Extracting text & computing FAISS embeddings...", text_color=THEME["text_muted"])

        def worker():
            try:
                res = rag_engine_instance.process_pdf(file_path)
                def on_success():
                    self.pdf_name_lbl.configure(text=f"📄 {res['file_name']}", text_color=THEME["text_primary"])
                    self.pdf_details_lbl.configure(
                        text=f"Pages: {res['total_pages']} | Vector Chunks: {res['total_chunks']}\nIndexed in FAISS Vector DB.",
                        text_color=THEME["accent_cyan"]
                    )
                    self.upload_btn.configure(state="normal", text="📤 Upload & Index PDF")
                    if self.on_pdf_loaded:
                        self.on_pdf_loaded(file_path)
                self.after(0, on_success)
            except Exception as e:
                def on_error(err=e):
                    self.upload_btn.configure(state="normal", text="📤 Upload & Index PDF")
                    self.pdf_name_lbl.configure(text="No PDF Loaded", text_color=THEME["text_muted"])
                    self.pdf_details_lbl.configure(text="Failed to index PDF.", text_color=THEME["text_muted"])
                    messagebox.showerror("PDF Processing Error", f"Failed to load PDF file:\n{str(err)}")
                self.after(0, on_error)

        threading.Thread(target=worker, daemon=True).start()


    def _on_reset_pdf_clicked(self):
        rag_engine_instance.reset()
        self.pdf_name_lbl.configure(text="No PDF Loaded", text_color=THEME["text_muted"])
        self.pdf_details_lbl.configure(
            text="Upload a PDF document to query with RAG.",
            text_color=THEME["text_muted"]
        )

    def _on_clear_memory_clicked(self):
        memory_engine_instance.clear()
        if self.on_memory_cleared:
            self.on_memory_cleared()
