"""Settings management for the email assistant."""

import os
import sys
import json
from tkinter import messagebox
from dotenv import load_dotenv

class SettingsManager:
    def __init__(self, log_callback):
        """Initialize the settings manager.
        
        Args:
            log_callback: Function to call for logging
        """
        self.log = log_callback
    
    def load_environment(self):
        """Load credentials from .env file.
        
        Returns:
            Dict of credentials
        """
        load_dotenv()
        creds = {
            'openai_key': os.getenv("OPENAI_API_KEY"),
            'gmail_user': os.getenv("GMAIL_USER"),
            'gmail_pass': os.getenv("GMAIL_APP_PASSWORD")
        }
        
        # Make sure we have what we need
        missing = [k for k, v in creds.items() if not v]
        if missing:
            messagebox.showerror("Missing Credentials", 
                               f"Missing credentials: {', '.join(missing)}")
            sys.exit(1)
            
        return creds
    
    def save_app_settings(self, root, dark_mode):
        """Save application settings for next time.
        
        Args:
            root: The main Tkinter window
            dark_mode: Boolean indicating if dark mode is enabled
        """
        settings = {
            "window": {
                "width": root.winfo_width(),
                "height": root.winfo_height(),
                "x": root.winfo_x(),
                "y": root.winfo_y()
            },
            "dark_mode": dark_mode,
        }
        
        try:
            with open("app_settings.json", "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            self.log(f"Could not save settings: {str(e)}")
    
    def load_app_settings(self, root, dark_mode_var, toggle_dark_mode_callback):
        """Load application settings from previous session.
        
        Args:
            root: The main Tkinter window
            dark_mode_var: Tkinter variable for dark mode
            toggle_dark_mode_callback: Callback to apply dark mode
        """
        try:
            with open("app_settings.json", "r") as f:
                settings = json.load(f)
                
            # Apply window settings
            if "window" in settings:
                w = settings["window"]["width"]
                h = settings["window"]["height"]
                x = settings["window"]["x"]
                y = settings["window"]["y"]
                root.geometry(f"{w}x{h}+{x}+{y}")
                
            # Apply dark mode
            if "dark_mode" in settings:
                dark_mode_var.set(settings["dark_mode"])
                toggle_dark_mode_callback()
                
        except FileNotFoundError:
            # No settings file yet, use defaults
            pass
        except Exception as e:
            self.log(f"Could not load settings: {str(e)}")