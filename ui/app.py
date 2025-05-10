"""
Voice Email Assistant - Main Application
----------------------------------------
The core UI and application logic for the Voice Email Assistant.
This module ties together all components to create a functional voice-controlled
email application with a modern, responsive interface.

Author: Abhish
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, BooleanVar
import threading
import logging

# Core components
from core.voice import VoiceHandler
from core.openai_assistant import EmailAssistant
from core.tts import TTSManager
from core.contacts import ContactManager
from core.settings import SettingsManager
from core.email_sender import EmailSender


class VoiceEmailApp:
    """
    Main application class for the Voice Email Assistant.
    
    Handles UI creation, event binding, and orchestration of the various
    services (voice recognition, AI, email sending, etc).
    """
    
    # Class constants
    LIGHT_THEME = {
        'bg': "#f0f0f0",
        'text': "#000000",
        'accent': "#4A6D8C",
        'frame': "#f0f0f0",
    }
    
    DARK_THEME = {
        'bg': "#2E2E2E",
        'text': "#FFFFFF",
        'accent': "#3A7BCA",
        'frame': "#383838",
    }
    
    def __init__(self, root):
        """
        Initialize the application.
        
        Args:
            root: The Tkinter root window
        """
        # -- Setup base window --
        self.root = root
        self.root.title("Voice Email Assistant")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        self.root.configure(bg=self.LIGHT_THEME['bg'])
        
        # Create placeholder for log_text widget that will be properly initialized later
        self.log_text = None
        
        # -- Initialize services --
        self._init_services()
        
        # -- Initialize state --
        self._init_application_state()
        
        # -- Build UI --
        self._create_widgets()
        
        # -- Load settings --
        self.settings_manager.load_app_settings(self.root, self.dark_mode, self.toggle_dark_mode)
        
        # -- Configure event handlers --
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Log successful launch
        self.log("Application initialized and ready")
    
    def _init_services(self):
        """Initialize all application services and dependencies."""
        # Settings must be loaded first to get credentials
        self.settings_manager = SettingsManager(self._console_log)
        self.credentials = self.settings_manager.load_environment()
        
        # Then initialize all other services
        self.contact_manager = ContactManager()
        self.contacts = self.contact_manager.load_contacts()
        self.email_assistant = EmailAssistant(self.credentials['openai_key'])
        self.voice_handler = VoiceHandler(self.process_voice_command, self.log)
        self.tts_manager = TTSManager()
        self.email_sender = EmailSender(self.credentials)
    
    def _init_application_state(self):
        """Initialize application state variables."""
        # UI state
        self.dark_mode = BooleanVar(value=False)
        self.mic_state = tk.StringVar(value="Start Listening")
        self.status_text = tk.StringVar(value="Ready")
        self.recipient_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        
        # Conversation context
        self.current_context = {
            "recipient": None,
            "subject": None,
            "partial_body": None,
            "in_conversation": False,
            "last_intent": None
        }
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        self._create_header()
        main_frame = self._create_main_content()
        self._create_left_panel(main_frame)
        self._create_email_compose_panel(main_frame)
        self._create_log_panel()
        
        # Apply styles
        self._configure_styles()
        
        # Add initial log entry after log panel is created
        self.log("Application started. Ready for voice commands.")
    
    def _create_header(self):
        """Create the application header with title and controls."""
        # Create header frame
        title_frame = tk.Frame(self.root, bg=self.LIGHT_THEME['accent'], pady=15)
        title_frame.pack(fill=tk.X)
        
        # Add title
        title_label = tk.Label(
            title_frame, 
            text="Voice Email Assistant", 
            font=("Arial", 18, "bold"), 
            fg="white", 
            bg=self.LIGHT_THEME['accent']
        )
        title_label.pack()
        
        # Add dark mode toggle
        dark_mode_frame = tk.Frame(title_frame, bg=self.LIGHT_THEME['accent'])
        dark_mode_frame.pack(anchor=tk.E, padx=10)
        
        dark_mode_cb = ttk.Checkbutton(
            dark_mode_frame, 
            text="Dark Mode", 
            variable=self.dark_mode, 
            command=self.toggle_dark_mode
        )
        dark_mode_cb.pack()
    
    def _create_main_content(self):
        """Create the main content area that will contain panels.
        
        Returns:
            tk.Frame: The main content frame
        """
        content_frame = tk.Frame(self.root, bg=self.LIGHT_THEME['bg'], pady=20, padx=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        return content_frame
    
    def _create_left_panel(self, parent_frame):
        """Create the left panel with microphone controls and contacts.
        
        Args:
            parent_frame: The parent frame to place this panel in
        """
        left_frame = tk.Frame(parent_frame, bg=self.LIGHT_THEME['bg'], padx=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Microphone button
        self.mic_button = ttk.Button(
            left_frame, 
            textvariable=self.mic_state,
            command=self.toggle_listening, 
            width=15
        )
        self.mic_button.pack(pady=10)
        
        # Status display
        status_frame = tk.LabelFrame(
            left_frame, 
            text="Status", 
            padx=10, 
            pady=10, 
            bg=self.LIGHT_THEME['bg']
        )
        status_frame.pack(fill=tk.X, pady=10)
        
        status_label = tk.Label(
            status_frame, 
            textvariable=self.status_text, 
            bg=self.LIGHT_THEME['bg'], 
            wraplength=200
        )
        status_label.pack(fill=tk.X)
        
        # Contacts section
        self._create_contacts_section(left_frame)
    
    def _create_contacts_section(self, parent_frame):
        """Create the contacts section with list and add button.
        
        Args:
            parent_frame: The parent frame to place this section in
        """
        contact_frame = tk.LabelFrame(
            parent_frame, 
            text="Contacts", 
            padx=10, 
            pady=10, 
            bg=self.LIGHT_THEME['bg']
        )
        contact_frame.pack(fill=tk.X, pady=10, expand=True)
        
        # Contact list
        self.contact_listbox = tk.Listbox(contact_frame, height=10)
        self.contact_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Populate contact list
        self._update_contact_list()
        
        # Add contact button
        add_contact_btn = ttk.Button(
            contact_frame, 
            text="Add Contact", 
            command=self._show_add_contact_dialog
        )
        add_contact_btn.pack(fill=tk.X, pady=(10, 0))
    
    def _create_email_compose_panel(self, parent_frame):
        """Create the email composition panel.
        
        Args:
            parent_frame: The parent frame to place this panel in
        """
        right_frame = tk.Frame(parent_frame, bg=self.LIGHT_THEME['bg'], padx=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        email_frame = tk.LabelFrame(
            right_frame, 
            text="Compose Email", 
            padx=10, 
            pady=10, 
            bg=self.LIGHT_THEME['bg']
        )
        email_frame.pack(fill=tk.BOTH, expand=True)
        
        # To field
        tk.Label(email_frame, text="To:", bg=self.LIGHT_THEME['bg']).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        recipient_entry = ttk.Entry(email_frame, textvariable=self.recipient_var, width=40)
        recipient_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Subject field
        tk.Label(email_frame, text="Subject:", bg=self.LIGHT_THEME['bg']).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        subject_entry = ttk.Entry(email_frame, textvariable=self.subject_var, width=40)
        subject_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Message body
        tk.Label(email_frame, text="Message:", bg=self.LIGHT_THEME['bg']).grid(
            row=2, column=0, sticky=tk.NW, pady=5
        )
        self.message_text = scrolledtext.ScrolledText(email_frame, wrap=tk.WORD, height=10)
        self.message_text.grid(row=2, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Make message expandable
        email_frame.grid_rowconfigure(2, weight=1)
        email_frame.grid_columnconfigure(1, weight=1)
        
        # Action buttons
        button_frame = tk.Frame(email_frame, bg=self.LIGHT_THEME['bg'])
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        send_btn = ttk.Button(button_frame, text="Send Email", command=self._send_email)
        send_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(button_frame, text="Clear", command=self._clear_form)
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_log_panel(self):
        """Create the log panel at the bottom of the window."""
        log_frame = tk.LabelFrame(
            self.root, 
            text="Activity Log", 
            padx=10, 
            pady=10, 
            bg=self.LIGHT_THEME['bg']
        )
        log_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=5, 
            width=80, 
            wrap=tk.WORD,
            bg="white", 
            fg="black"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
    
    def _configure_styles(self):
        """Configure ttk styles for consistent look and feel."""
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background=self.LIGHT_THEME['accent'])
        style.map("TButton", 
                 background=[('active', self.LIGHT_THEME['accent'])],
                 foreground=[('active', 'white')])
    
    # =====================================================================
    # Voice control methods
    # =====================================================================
    
    def toggle_listening(self):
        """Toggle voice recognition on/off."""
        if self.voice_handler.is_listening():
            # Stop listening
            self.voice_handler.stop_listening()
            self.mic_state.set("Start Listening")
            self.status_text.set("Ready")
        else:
            # Start listening
            self.mic_state.set("Stop Listening")
            self.status_text.set("Listening...")
            self.tts_manager.speak("Listening")
            self.voice_handler.start_listening(self.root, self.status_text)
    
    def process_voice_command(self, command):
        """Process a recognized voice command.
        
        Args:
            command: The recognized command text
        """
        self.status_text.set("Processing...")
        
        # Build the context from previous interactions
        conversation_context = self._build_conversation_context()
        
        try:
            # Ask OpenAI to understand the command
            analysis = self.email_assistant.analyze_command(command, conversation_context)
            
            if analysis:
                self.log(f"AI understood: {analysis.get('explanation', 'No explanation provided')}")
                
                # Update conversation context
                self.current_context["in_conversation"] = True
                self.current_context["last_intent"] = analysis["intent"]
                
                # Dispatch to appropriate handler
                self._handle_intent(analysis)
            else:
                # AI didn't return valid JSON or there was an error
                self._handle_command_fallback(command)
            
        except Exception as e:
            self.log(f"Error processing command: {str(e)}")
            self.status_text.set("Error occurred")
    
    def _handle_intent(self, analysis):
        """Handle an intent based on AI analysis.
        
        Args:
            analysis: The AI analysis of the command
        """
        intent = analysis["intent"]
        
        # Use dictionary-based dispatching for cleaner code than if/elif chains
        intent_handlers = {
            "COMPOSE_EMAIL": lambda: self._handle_compose_intent(analysis),
            "CONTINUE_BODY": lambda: self._handle_continue_body_intent(analysis),
            "SEND_EMAIL": lambda: self._handle_send_intent(),
            "CLEAR_FORM": lambda: self._handle_clear_intent(),
            "ADD_CONTACT": lambda: self._show_add_contact_dialog(),
            "HELP": lambda: self._show_help(),
            "UNKNOWN": lambda: self._handle_unknown_intent()
        }
        
        # Get the handler function for this intent (default to unknown if not found)
        handler = intent_handlers.get(intent, intent_handlers["UNKNOWN"])
        
        # Execute the handler
        handler()
    
    def _handle_compose_intent(self, analysis):
        """Handle intent to compose a new email.
        
        Args:
            analysis: The AI analysis of the command
        """
        # Process recipient
        if analysis.get("recipient"):
            self.current_context["recipient"] = analysis["recipient"]
            # Try to find recipient in contacts or use as is
            recipient_email = self.contacts.get(analysis["recipient"].lower(), analysis["recipient"])
            self.recipient_var.set(recipient_email)
            self.log(f"Setting recipient: {recipient_email}")
        
        # Process subject
        if analysis.get("subject"):
            self.current_context["subject"] = analysis["subject"]
            self.subject_var.set(analysis["subject"])
            self.log(f"Setting subject: {analysis['subject']}")
        
        # Process body
        if analysis.get("body"):
            self.current_context["partial_body"] = analysis["body"]
            self.message_text.delete(1.0, tk.END)
            self.message_text.insert(tk.END, analysis["body"])
            self.log(f"Setting message body")
        
        # Tell the user what we still need
        self._provide_next_step_guidance()
    
    def _handle_continue_body_intent(self, analysis):
        """Handle intent to continue or modify the message body.
        
        Args:
            analysis: The AI analysis of the command
        """
        current_text = self.message_text.get(1.0, tk.END).strip()
        
        if analysis.get("continue_previous", False) and current_text:
            # Append to existing text
            new_text = current_text + " " + analysis.get("body", "")
            self.message_text.delete(1.0, tk.END)
            self.message_text.insert(tk.END, new_text)
            self.current_context["partial_body"] = new_text
            self.log("Appended to message body")
        else:
            # Replace with new text
            self.message_text.delete(1.0, tk.END)
            self.message_text.insert(tk.END, analysis.get("body", ""))
            self.current_context["partial_body"] = analysis.get("body", "")
            self.log("Updated message body")
        
        self.status_text.set("Message updated")
        self.tts_manager.speak("Message updated")
    
    def _handle_send_intent(self):
        """Handle intent to send the current email."""
        self._send_email()
        self._reset_conversation_context()
    
    def _handle_clear_intent(self):
        """Handle intent to clear the form."""
        self._clear_form()
        self.status_text.set("Form cleared")
        self.tts_manager.speak("Form cleared")
        self._reset_conversation_context()
    
    def _handle_unknown_intent(self):
        """Handle when we don't know what the user wants."""
        if not self.current_context["in_conversation"]:
            # First interaction - give general guidance
            self.log("I'm not sure what you want to do. Try saying 'Send an email to [name]'")
            self.status_text.set("Try 'Send an email to [name]'")
            self.tts_manager.speak("I'm not sure what you want to do. Try sending an email to someone.")
        else:
            # Try to relate to current context
            self.log("I didn't understand that in the context of your email. Please try again.")
            self.status_text.set("Please try again")
            self.tts_manager.speak("I didn't understand that in the context of your email.")
    
    def _handle_command_fallback(self, command):
        """Handle commands when AI parsing fails.
        
        Args:
            command: The original command text
        """
        command_lower = command.lower()
        
        # Try to handle common commands directly
        if "send" in command_lower and "email" in command_lower:
            # Try to handle a send email command manually
            parts = command_lower.split("to")
            if len(parts) > 1:
                recipient = parts[1].strip().split(" ")[0]
                self.recipient_var.set(recipient)
                self.log(f"Manually detected recipient: {recipient}")
                self.status_text.set("I need more details")
                self.tts_manager.speak("I need more details for your email")
        
        elif "send" in command_lower and self.recipient_var.get():
            # Try to send the current email
            self._send_email()
            
        elif "clear" in command_lower or "start over" in command_lower:
            # Clear the form
            self._clear_form()
            self.status_text.set("Form cleared")
            self.tts_manager.speak("Form cleared")
            self._reset_conversation_context()
        
        else:
            self.status_text.set("I didn't understand that")
            self.tts_manager.speak("I didn't understand that command")
    
    def _show_help(self):
        """Show help information in the log."""
        help_message = "You can say things like:\n"
        help_message += "- 'Send an email to John about the project'\n"
        help_message += "- 'The meeting is scheduled for Thursday'\n"
        help_message += "- 'Send it now'\n"
        help_message += "- 'Start over'\n"
        help_message += "- 'Add Sarah to my contacts'"
        
        self.log(help_message)
        self.status_text.set("Help info in log")
        self.tts_manager.speak("I've shown some help in the log")
    
    def _build_conversation_context(self):
        """Build context string from the current conversation state.
        
        Returns:
            str: The context string for the AI
        """
        if not self.current_context["in_conversation"]:
            return ""
        
        context_parts = []
        if self.current_context["recipient"]:
            context_parts.append(f"Recipient: {self.current_context['recipient']}")
        if self.current_context["subject"]:
            context_parts.append(f"Subject: {self.current_context['subject']}")
        if self.current_context["partial_body"]:
            context_parts.append(f"Previous message content: {self.current_context['partial_body']}")
        
        if context_parts:
            return "Current email draft: " + "; ".join(context_parts) + ". "
        return ""
    
    def _provide_next_step_guidance(self):
        """Tell the user what information is still needed."""
        missing = []
        
        if not self.recipient_var.get():
            missing.append("recipient")
        if not self.subject_var.get():
            missing.append("subject")
        if not self.message_text.get(1.0, tk.END).strip():
            missing.append("message body")
        
        if missing:
            missing_str = ", ".join(missing)
            guidance = f"I need your {missing_str}"
            self.status_text.set(guidance)
            self.tts_manager.speak(guidance)
        else:
            self.status_text.set("Your email is ready to send. Say 'send it' when ready.")
            self.tts_manager.speak("Your email is ready. Say send it when ready.")
    
    def _reset_conversation_context(self):
        """Reset the conversation context."""
        self.current_context = {
            "recipient": None,
            "subject": None, 
            "partial_body": None,
            "in_conversation": False,
            "last_intent": None
        }
    
    # =====================================================================
    # Email functions
    # =====================================================================
    
    def _send_email(self):
        """Validate and send the email."""
        recipient = self.recipient_var.get().strip()
        subject = self.subject_var.get().strip()
        body = self.message_text.get(1.0, tk.END).strip()
        
        # Perform validation
        if not self._validate_email_form(recipient, body):
            return
            
        # Ask for confirmation
        if not self._confirm_send_email(recipient, subject, body):
            return
            
        # Send the email
        success, message = self.email_sender.send_email(recipient, subject, body)
        
        if success:
            messagebox.showinfo("Success", "Email sent successfully!")
            self.log(f"Email sent to {recipient}")
            self.tts_manager.speak("Email sent successfully")
            self._clear_form()
        else:
            messagebox.showerror("Error", f"Failed to send email: {message}")
            self.log(f"Failed to send email: {message}")
    
    def _validate_email_form(self, recipient, body):
        """Validate the email form.
        
        Args:
            recipient: The recipient string
            body: The email body
            
        Returns:
            bool: True if the form is valid, False otherwise
        """
        if not recipient:
            messagebox.showerror("Error", "Recipient is required")
            return False
            
        # Check if recipient is valid
        if not self.email_sender.is_valid_email(recipient):
            # Maybe it's a contact name
            email = self.contacts.get(recipient.lower())
            if not email:
                messagebox.showerror("Error", f"Invalid email address: {recipient}")
                return False
            self.recipient_var.set(email)  # Update the field with resolved email
        
        # Make sure we have a message body
        if not body:
            messagebox.showerror("Error", "Email body cannot be empty")
            return False
            
        return True
    
    def _confirm_send_email(self, recipient, subject, body):
        """Ask for confirmation before sending.
        
        Args:
            recipient: The recipient email
            subject: The email subject
            body: The email body
            
        Returns:
            bool: True if confirmed, False otherwise
        """
        # Truncate the body for the confirmation dialog if it's too long
        preview = body[:50] + ("..." if len(body) > 50 else "")
        
        return messagebox.askyesno(
            "Confirm", 
            f"Send email to {recipient}?\n\nSubject: {subject}\n\nMessage: {preview}"
        )
    
    def _clear_form(self):
        """Clear all form fields."""
        self.recipient_var.set("")
        self.subject_var.set("")
        self.message_text.delete(1.0, tk.END)
        self.log("Form cleared")
    
    # =====================================================================
    # Contact management
    # =====================================================================
    
    def _update_contact_list(self):
        """Refresh the contact list display."""
        self.contact_listbox.delete(0, tk.END)
        for name, email in self.contacts.items():
            self.contact_listbox.insert(tk.END, f"{name}: {email}")
    
    def _show_add_contact_dialog(self):
        """Show dialog to add a new contact."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Contact")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Setup widget variables
        name_var = tk.StringVar()
        email_var = tk.StringVar()
        
        # Create fields
        tk.Label(dialog, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=20)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        
        tk.Label(dialog, text="Email:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        email_entry = ttk.Entry(dialog, textvariable=email_var, width=20)
        email_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Save contact function
        def save_contact():
            name = name_var.get().strip().lower()
            email = email_var.get().strip()
            
            if not name or not email:
                messagebox.showerror("Error", "Name and email are required")
                return
                
            if not self.email_sender.is_valid_email(email):
                messagebox.showerror("Error", "Invalid email address")
                return
                
            self.contacts[name] = email
            self.contact_manager.save_contacts(self.contacts)
            self._update_contact_list()
            self.log(f"Added contact: {name} ({email})")
            dialog.destroy()
        
        # Add save button
        save_btn = ttk.Button(dialog, text="Save", command=save_contact)
        save_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Focus on first field
        name_entry.focus_set()
    
    # =====================================================================
    # UI utility methods
    # =====================================================================
    
    def log(self, message):
        """Add a message to the log window.
        
        Args:
            message: The message to log
        """
        if self.log_text is None:
            # Fall back to console log if the UI hasn't been built yet
            self._console_log(message)
            return
            
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)  # Auto-scroll to the latest entry
            self.log_text.config(state=tk.DISABLED)
            
            # Force update the display
            self.root.update_idletasks()
            
            # Also log to console for debugging
            self._console_log(message)
        except Exception as e:
            self._console_log(f"Error writing to log: {e}")
            self._console_log(f"Original message: {message}")
    
    def _console_log(self, message):
        """Log a message to the console.
        
        Args:
            message: The message to log
        """
        print(f"LOG: {message}")
    
    def toggle_dark_mode(self):
        """Switch between light and dark mode."""
        # Determine theme
        theme = self.DARK_THEME if self.dark_mode.get() else self.LIGHT_THEME
        
        # Update colors for all widgets
        self.root.configure(bg=theme['bg'])
        
        # Update frames
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
                widget.configure(bg=theme['frame'])
                
                # Update labels and other widgets inside frames
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=theme['frame'], fg=theme['text'])
                    elif isinstance(child, scrolledtext.ScrolledText):
                        child.configure(bg=theme['bg'], fg=theme['text'])
        
        # Update title frame specially
        title_frame = self.root.winfo_children()[0]
        title_frame.configure(bg=theme['accent'])
        for child in title_frame.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=theme['accent'], fg="#FFFFFF")
        
        # Update the log and message text areas
        self.log_text.configure(bg=theme['bg'], fg=theme['text'])
        self.message_text.configure(bg=theme['bg'], fg=theme['text'])
        
        self.log(f"{'Dark' if self.dark_mode.get() else 'Light'} mode activated")
    
    def _on_closing(self):
        """Handle window closing event."""
        self.settings_manager.save_app_settings(self.root, self.dark_mode.get())
        self.root.destroy()