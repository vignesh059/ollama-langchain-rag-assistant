"""
Main Application Window for Chatbot Desktop UI.
Integrates Sidebar, ChatView, InputBar, and Multi-Threaded Query Processing.
"""

import threading
import customtkinter as ctk
from typing import Optional

from ui.styles import THEME, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_SMALL
from ui.components.sidebar import Sidebar
from ui.components.chat_view import ChatView
from ui.components.input_bar import InputBar
from backend.agent_engine import agent_engine_instance
from backend.memory_engine import memory_engine_instance
from config import DEFAULT_SYSTEM_PROMPT, DEFAULT_MODEL


class ChatbotMainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Config
        self.title("AI Chatbot - LangChain • Ollama • RAG • Tools • Memory")
        self.geometry("1100 x 720")
        self.minsize(900, 600)

        # Set CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=THEME["bg_main"])

        self.selected_model = DEFAULT_MODEL

        self._build_layout()
        self._add_welcome_message()

    def _build_layout(self):
        # 1. Left Sidebar
        self.sidebar = Sidebar(
            self,
            on_pdf_loaded_callback=self._handle_pdf_loaded,
            on_memory_cleared_callback=self._handle_memory_cleared,
            on_model_changed_callback=self._handle_model_changed
        )
        self.sidebar.pack(side="left", fill="y")

        # 2. Right Main Chat Area Frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Chat Top Header Bar
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=THEME["bg_sidebar"], height=50, corner_radius=0)
        header_frame.pack(side="top", fill="x")

        header_lbl = ctk.CTkLabel(
            header_frame,
            text="💬 Chat Assistant",
            font=FONT_SUBTITLE,
            text_color=THEME["text_primary"]
        )
        header_lbl.pack(side="left", padx=16, pady=10)

        self.model_status_lbl = ctk.CTkLabel(
            header_frame,
            text=f"Active Model: {self.selected_model}",
            font=FONT_SMALL,
            text_color=THEME["accent_cyan"]
        )
        self.model_status_lbl.pack(side="right", padx=16, pady=10)

        # Chat View Component
        self.chat_view = ChatView(self.main_frame)
        self.chat_view.pack(side="top", fill="both", expand=True, padx=12, pady=12)

        # Input Bar Component
        self.input_bar = InputBar(
            self.main_frame, 
            on_send_callback=self._handle_user_send,
            on_attach_callback=self._handle_input_attach,
            on_clear_pdf_callback=self._handle_input_clear_pdf
        )
        self.input_bar.pack(side="bottom", fill="x", padx=12, pady=(0, 12))

    def _add_welcome_message(self):
        welcome_text = (
            "Hello! I am your AI Chatbot powered by **Ollama**, **LangChain**, and local tools.\n\n"
            "✨ **Features You Can Try**:\n"
            "1. **Attendance Calculator**: Type *'I present 18 classes out of 24, what is my percentage?'*\n"
            "2. **Wikipedia Search**: Type *'Search wikipedia for Artificial Intelligence'*\n"
            "3. **PDF RAG QA**: Upload a PDF file in the sidebar and ask questions about its content!\n"
            "4. **Conversation Memory**: I remember our previous questions and context."
        )
        self.chat_view.add_message(welcome_text, is_user=False)

    def _handle_user_send(self, user_text: str):
        # Add user message to GUI immediately
        self.chat_view.add_message(user_text, is_user=True)

        # Disable input while processing
        self.input_bar.set_state(enabled=False)

        # Run query in background thread so Tkinter UI stays responsive
        threading.Thread(
            target=self._process_query_async,
            args=(user_text, self.selected_model),
            daemon=True
        ).start()

    def _process_query_async(self, user_text: str, model_name: str):
        tool_used_holder = [None]

        def on_tool(tool_name: str):
            tool_used_holder[0] = tool_name

        try:
            res = agent_engine_instance.process_query(
                user_input=user_text,
                model_name=model_name,
                on_tool_called=on_tool
            )
            ai_text = res.get("response", "No response generated.")
            tool_name = res.get("tool_used") or tool_used_holder[0]
        except Exception as e:
            ai_text = f"Error processing query: {str(e)}"
            tool_name = None

        # Update GUI on main thread
        self.after(0, lambda: self._on_query_complete(ai_text, tool_name))

    def _on_query_complete(self, ai_text: str, tool_name: Optional[str]):
        self.chat_view.add_message(ai_text, is_user=False, tool_name=tool_name)
        self.input_bar.set_state(enabled=True)

    def _handle_pdf_loaded(self, file_path: str):
        doc_name = self.sidebar.pdf_name_lbl.cget("text")
        self.input_bar.show_attached_file(doc_name)
        self.chat_view.add_message(
            f"✅ **PDF Successfully Uploaded & Indexed**!\n{doc_name}\n"
            f"🔒 **STRICT PDF MODE ACTIVATED**: Answers will be given strictly from this document only.",
            is_user=False,
            tool_name="PDF Search (RAG)"
        )

    def _handle_input_attach(self):
        self.sidebar._on_upload_pdf_clicked()

    def _handle_input_clear_pdf(self):
        self.sidebar._on_reset_pdf_clicked()
        self.input_bar.hide_attached_file()
        self.chat_view.add_message("🗑️ Document detached. Returned to general chatbot mode.", is_user=False)

    def _handle_memory_cleared(self):
        self.chat_view.clear()
        self.input_bar.hide_attached_file()
        self._add_welcome_message()
        self.chat_view.add_message("🧹 Conversation memory has been cleared!", is_user=False)

    def _handle_model_changed(self, model_name: str):
        self.selected_model = model_name
        self.model_status_lbl.configure(text=f"Active Model: {self.selected_model}")
