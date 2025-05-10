"""Voice recognition handler for the email assistant."""

import threading
import speech_recognition as sr

class VoiceHandler:
    def __init__(self, command_callback, log_callback):
        """Initialize the voice recognition handler.
        
        Args:
            command_callback: Function to call when a command is recognized
            log_callback: Function to call for logging
        """
        self.recognizer = sr.Recognizer()
        self.listening = False
        self.recognition_thread = None
        self.command_callback = command_callback
        self.log = log_callback
    
    def is_listening(self):
        """Return whether we're currently listening."""
        return self.listening
    
    def start_listening(self, root, status_text):
        """Start the voice recognition thread."""
        self.listening = True
        self.recognition_thread = threading.Thread(target=self._listen_for_voice, args=(root, status_text))
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
    
    def stop_listening(self):
        """Stop the voice recognition thread."""
        self.listening = False
    
    def _listen_for_voice(self, root, status_text):
        """Background thread for voice recognition."""
        with sr.Microphone() as source:
            self.log("Adjusting for ambient noise...")
            try:
                # First calibrate for background noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                root.update_idletasks()
                
                # Main listening loop
                while self.listening:
                    try:
                        status_text.set("Listening...")
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                        status_text.set("Processing speech...")
                        
                        # Convert speech to text
                        text = self.recognizer.recognize_google(audio)
                        self.log(f"You said: {text}")
                        
                        # Process what was said
                        self.command_callback(text)
                        
                    except sr.WaitTimeoutError:
                        # Nothing was said
                        if self.listening:
                            status_text.set("No speech detected. Still listening...")
                    except sr.UnknownValueError:
                        # Couldn't understand what was said
                        if self.listening:
                            self.log("Could not understand audio")
                            status_text.set("Didn't catch that. Please try again...")
                    except sr.RequestError:
                        # Google API problem
                        self.log("Could not request results from Google Speech Recognition")
                        status_text.set("Speech service unavailable")
                        self.listening = False
                    except Exception as e:
                        # Unexpected error
                        self.log(f"Error: {str(e)}")
                        status_text.set("Error occurred")
            except Exception as e:
                # Microphone or setup error
                self.log(f"Microphone error: {str(e)}")
                status_text.set("Ready")
                self.listening = False