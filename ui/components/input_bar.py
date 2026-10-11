"""
Input Bar Component with Multiline Textbox, Attachment Upload Button, and File Status Indicator.
"""

import customtkinter as ctk
from typing import Callable, Optional
from ui.styles import THEME, FONT_BODY, FONT_BOLD, FONT_SMALL


class InputBar(ctk.CTkFrame):
    def __init__(
        self, 
        master, 
        on_send_callback: Callable[[str], None],
        on_attach_callback: Optional[Callable[[], None]] = None,
        on_clear_pdf_callback: Optional[Callable[[], None]] = None
    ):
        super().__init__(
            master, 
            fg_color=THEME["bg_input"], 
            corner_radius=12,
            border_width=1,
            border_color=THEME["border_color"]
        )
        self.on_send = on_send_callback
        self.on_attach = on_attach_callback
        self.on_clear_pdf = on_clear_pdf_callback

        self._build_ui()

    def _build_ui(self):
        # 1. Attachment Bar (shows attached PDF badge when active)
        self.attachment_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.attached_lbl = ctk.CTkLabel(
            self.attachment_frame,
            text="📄 Attached Document: sample.pdf",
            font=FONT_SMALL,
            text_color=THEME["accent_cyan"]
        )
        self.attached_lbl.pack(side="left", padx=8, pady=(4, 0))

        self.detach_btn = ctk.CTkButton(
            self.attachment_frame,
            text="✖ Remove PDF",
            font=FONT_SMALL,
            width=70,
            height=20,
            fg_color="#991B1B",
            hover_color="#7F1D1D",
            text_color="#FFFFFF",
            command=self._trigger_clear_pdf
        )
        self.detach_btn.pack(side="left", padx=6, pady=(4, 0))

        # 2. Main Input & Controls Row
        self.input_row = ctk.CTkFrame(self, fg_color="transparent")
        self.input_row.pack(fill="x", expand=True, padx=4, pady=4)

        # Attachment Icon Button (📎)
        self.attach_btn = ctk.CTkButton(
            self.input_row,
            text="📎",
            font=("Segoe UI", 18),
            width=42,
            height=42,
            fg_color=THEME["bg_card"],
            hover_color=THEME["accent_violet"],
            text_color=THEME["accent_cyan"],
            command=self._trigger_attach
        )
        self.attach_btn.pack(side="left", padx=(8, 4), pady=8, anchor="s")

        # Multiline Textbox
        self.textbox = ctk.CTkTextbox(
            self.input_row,
            font=FONT_BODY,
            fg_color="transparent",
            text_color=THEME["text_primary"],
            wrap="word",
            height=50
        )
        self.textbox.pack(side="left", fill="both", expand=True, padx=4, pady=6)
        self.textbox.bind("<Return>", self._on_enter_pressed)

        # Send Button Container
        btn_container = ctk.CTkFrame(self.input_row, fg_color="transparent")
        btn_container.pack(side="right", padx=(4, 8), pady=6, anchor="s")

        self.send_btn = ctk.CTkButton(
            btn_container,
            text="Send ➔",
            font=FONT_BOLD,
            width=80,
            height=42,
            fg_color=THEME["accent_cyan"],
            hover_color=THEME["accent_violet"],
            text_color="#000000",
            command=self._trigger_send
        )
        self.send_btn.pack(side="top")

    def show_attached_file(self, filename: str):
        """Displays attached file indicator badge above typing area."""
        self.attached_lbl.configure(text=f"📄 Active PDF (Strict Mode): {filename}")
        self.attachment_frame.pack(side="top", fill="x", padx=8, pady=(4, 0), before=self.input_row)

    def hide_attached_file(self):
        """Hides attached file indicator badge."""
        self.attachment_frame.pack_forget()

    def _trigger_attach(self):
        if self.on_attach:
            self.on_attach()

    def _trigger_clear_pdf(self):
        self.hide_attached_file()
        if self.on_clear_pdf:
            self.on_clear_pdf()

    def _on_enter_pressed(self, event):
        if not (event.state & 0x1):  # Shift key mask
            self._trigger_send()
            return "break"

    def _trigger_send(self):
        text = self.textbox.get("1.0", "end-1c").strip()
        if text:
            self.textbox.delete("1.0", "end")
            self.on_send(text)

    def set_state(self, enabled: bool):
        """Enables or disables send button during LLM processing."""
        state = "normal" if enabled else "disabled"
        self.send_btn.configure(state=state)
        self.attach_btn.configure(state=state)
        if enabled:
            self.send_btn.configure(text="Send ➔")
        else:
            self.send_btn.configure(text="Thinking...")
