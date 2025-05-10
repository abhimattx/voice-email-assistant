# 🔊 Voice Email Assistant

> Send Gmail messages entirely by voice using AI-powered natural language understanding

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/AI-OpenAI%20GPT-blueviolet)](https://openai.com/)

A seamless desktop application that understands your spoken commands to compose and send emails. Perfect for accessibility, multitasking, or when you simply prefer speaking over typing.

## 📱 Demo Screenshot

![Voice Email Assistant Interface](./assets/interface_screenshot.png)

*The Voice Email Assistant provides an intuitive interface for hands-free email composition*

## ✨ Features

![Features](https://via.placeholder.com/800x400?text=Voice+Email+Assistant+Demo)

- **🎙️ Voice-First Interaction** - Compose emails hands-free with advanced speech recognition
- **🧠 AI-Powered Understanding** - GPT-4 contextually processes your natural language commands
- **📧 Gmail Integration** - Send emails securely through your Gmail account
- **👥 Contact Management** - Save and retrieve contacts with simple voice commands
- **🔄 Contextual Memory** - Multi-turn conversations with context retention
- **🌓 Dark/Light Theme** - Choose your preferred visual experience
- **💾 Persistent Settings** - App remembers your preferences between sessions
- **🗣️ Voice Feedback** - Audible confirmations keep you informed

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Gmail account with [App Password](https://support.google.com/accounts/answer/185833) (requires 2FA)
- OpenAI API key

### Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/abhimattx/voice-email-assistant.git
    cd voice-email-assistant
    ```

2. **Set up virtual environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate    # macOS/Linux
    .\.venv\Scripts\activate     # Windows
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure your credentials**
    
    Create a `.env` file:
    ```
    OPENAI_API_KEY=sk-...
    GMAIL_USER=your@gmail.com
    GMAIL_APP_PASSWORD=your-app-password
    ```

5. **Launch the application**
    ```bash
    python main.py
    ```

## 🎯 How to Use

1. Click the **Start Listening** button or use the keyboard shortcut
2. **Speak naturally** using commands like:
    - "Send an email to Alex about the project meeting tomorrow"
    - "Add Maria to my contacts: maria@example.com"
    - "Read back what I have so far"
    - "Send the email now"
3. Review the populated fields and confirm before sending
4. Use voice commands or buttons to navigate the interface

<details>
<summary><strong>🎮 Voice Command Examples</strong></summary>

| Command | Action |
|---------|--------|
| "Email John about the project update" | Creates new email with subject |
| "The meeting is scheduled for Friday at 2 PM" | Adds to email body |
| "Add Tom to contacts: tom@example.com" | Creates new contact |
| "List my contacts" | Shows all contacts |
| "Clear everything" | Resets the form |
| "Switch to dark mode" | Changes theme |
| "Send this email" | Transmits the message |

</details>

## 🏗️ Project Structure

```
voice_email_assistant/
├── main.py                # Entry point
├── ui/
│   └── app.py             # Tkinter GUI implementation
└── core/
     ├── voice.py           # Speech recognition
     ├── openai_assistant.py# GPT integration
     ├── tts.py             # Text-to-speech
     ├── contacts.py        # Contact management
     ├── settings.py        # App settings
     └── email_sender.py    # Gmail integration
```

## 🔧 Advanced Configuration

- **Speech Recognition**: Configure alternative engines in `core/voice.py`
- **LLM Integration**: Adjust prompts and parameters in `core/openai_assistant.py`
- **UI Customization**: Modify themes and layout in `ui/app.py`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <i>Built with ❤️ by <a href="https://github.com/abhimattx">Abhishek Singh</a> | 
  <a href="https://www.linkedin.com/in/abhimattx/">LinkedIn</a> | 
  <a href="https://abhimattx.github.io/">Portfolio</a></i>
</p>