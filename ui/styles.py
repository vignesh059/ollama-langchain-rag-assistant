"""
UI Styles, themes, and design system configuration.
"""

# Visual Theme Tokens
THEME = {
    # Main Colors
    "bg_main": "#0F172A",          # Deep navy/slate window background
    "bg_sidebar": "#1E293B",       # Sidebar container background
    "bg_card": "#1E293B",          # Card background
    "bg_chat": "#0F172A",          # Scrollable chat area background
    "bg_input": "#1E293B",         # Input area background
    
    # Message Bubbles
    "user_bubble_bg": "#2563EB",   # Vibrant blue for user messages
    "user_bubble_fg": "#FFFFFF",
    "ai_bubble_bg": "#334155",     # Slate dark for AI messages
    "ai_bubble_fg": "#F8FAFC",
    
    # Tool Badges & Accents
    "accent_cyan": "#06B6D4",      # General vibrant accent
    "accent_violet": "#8B5CF6",    # Secondary accent
    "tool_wiki_bg": "#D97706",     # Amber badge for Wikipedia tool
    "tool_att_bg": "#10B981",      # Emerald badge for Attendance tool
    "tool_pdf_bg": "#6366F1",      # Indigo badge for PDF RAG tool
    "status_connected": "#22C55E", # Green light
    "status_disconnected": "#EF4444", # Red light
    
    # Text colors
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    
    # Border & Dividers
    "border_color": "#334155",
}

FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
FONT_BODY = (FONT_FAMILY, 12, "normal")
FONT_BOLD = (FONT_FAMILY, 12, "bold")
FONT_SMALL = (FONT_FAMILY, 10, "normal")
FONT_MONO = ("Consolas", 11, "normal")
