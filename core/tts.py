"""Text-to-speech manager for the email assistant."""

import threading
import pyttsx3

class TTSManager:
    def __init__(self):
        """Initialize the text-to-speech engine."""
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed
    
    def speak(self, text):
        """Speak the given text with error handling.
        
        Args:
            text: The text to speak
        """
        # Run in a separate thread to avoid freezing the UI
        threading.Thread(target=self._tts_thread, args=(text,), daemon=True).start()
    
    def _tts_thread(self, text):
        """Background thread for text-to-speech.
        
        Args:
            text: The text to speak
        """
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except RuntimeError as e:
            # Handle the 'run loop already started' error
            print(f"TTS error: {e}")
            # Recreate the engine if needed
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as inner_e:
                print(f"TTS reinit error: {inner_e}")
        except Exception as e:
            print(f"TTS error: {e}")