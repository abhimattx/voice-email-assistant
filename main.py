"""
Voice-Activated Email Assistant
-------------------------------
Send emails using voice commands with a simple GUI interface.

Features:
- Voice recognition for hands-free email composition
- Natural language understanding with OpenAI
- Contact management
- Dark/light theme
- Text-to-speech feedback
"""

import tkinter as tk
from ui.app import VoiceEmailApp

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceEmailApp(root)
    root.mainloop()