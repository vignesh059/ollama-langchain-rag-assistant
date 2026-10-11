"""
Scrollable Chat Transcript Component with Custom Message Bubbles and Tool Invocation Badges.
"""

import customtkinter as ctk
from typing import Optional
from ui.styles import THEME, FONT_BODY, FONT_BOLD, FONT_SMALL, FONT_SUBTITLE


class ToolBadge(ctk.CTkFrame):
    """Visual badge pill displaying tool invocation info."""
    def __init__(self, master, tool_name: str):
        # Choose pill color based on tool type
        if "Wikipedia" in tool_name:
            bg_color = THEME["tool_wiki_bg"]
            icon = "🌐"
        elif "Attendance" in tool_name:
            bg_color = THEME["tool_att_bg"]
            icon = "📊"
        elif "PDF" in tool_name or "RAG" in tool_name:
            bg_color = THEME["tool_pdf_bg"]
            icon = "📄"
        else:
            bg_color = THEME["accent_violet"]
            icon = "🛠️"

        super().__init__(
            master, 
            fg_color=bg_color, 
            corner_radius=12, 
            border_width=0
        )
        
        lbl = ctk.CTkLabel(
            self,
            text=f"{icon} Tool Activated: {tool_name}",
            font=FONT_SMALL,
            text_color="#FFFFFF",
            padx=10,
            pady=2
        )
        lbl.pack(padx=6, pady=2)


class MessageBubble(ctk.CTkFrame):
    """Renders a user or AI speech bubble."""
    def __init__(
        self, 
        master, 
        text: str, 
        is_user: bool, 
        tool_name: Optional[str] = None
    ):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="x", padx=12, pady=6)

        align = "e" if is_user else "w"
        bubble_bg = THEME["user_bubble_bg"] if is_user else THEME["ai_bubble_bg"]
        text_fg = THEME["user_bubble_fg"] if is_user else THEME["ai_bubble_fg"]
        sender_title = "You" if is_user else "AI Assistant"

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(anchor=align, padx=4)

        # Sender Label
        sender_lbl = ctk.CTkLabel(
            container, 
            text=sender_title, 
            font=FONT_SMALL, 
            text_color=THEME["text_muted"]
        )
        sender_lbl.pack(anchor=align, padx=6, pady=(0, 2))

        # Optional Tool Badge for AI messages
        if not is_user and tool_name:
            badge = ToolBadge(container, tool_name)
            badge.pack(anchor=align, padx=4, pady=(0, 4))

        # Main Text Bubble
        bubble = ctk.CTkFrame(
            container, 
            fg_color=bubble_bg, 
            corner_radius=14
        )
        bubble.pack(anchor=align)

        # Text Content
        msg_lbl = ctk.CTkLabel(
            bubble,
            text=text,
            font=FONT_BODY,
            text_color=text_fg,
            wraplength=520,
            justify="left",
            anchor="w"
        )
        msg_lbl.pack(padx=14, pady=10)


class ChatView(ctk.CTkScrollableFrame):
    """Scrollable container for all chat bubbles."""
    def __init__(self, master):
        super().__init__(
            master,
            fg_color=THEME["bg_chat"],
            scrollbar_button_color=THEME["border_color"],
            scrollbar_button_hover_color=THEME["accent_cyan"]
        )

    def add_message(self, text: str, is_user: bool, tool_name: Optional[str] = None):
        """Appends a new message bubble to the chat."""
        bubble = MessageBubble(self, text, is_user, tool_name)
        # Force scroll update to bottom
        self._parent_canvas.yview_moveto(1.0)

    def clear(self):
        """Clears all message bubbles from view."""
        for child in self.winfo_children():
            child.destroy()
