"""Contact management for the email assistant."""

import json

class ContactManager:
    def __init__(self):
        """Initialize the contact manager."""
        pass
    
    def load_contacts(self):
        """Load contacts from JSON file.
        
        Returns:
            Dict of contacts (name -> email)
        """
        try:
            with open("contacts.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # First run or file deleted
            return {}
    
    def save_contacts(self, contacts):
        """Save contacts dict to JSON file.
        
        Args:
            contacts: Dict of contacts (name -> email)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open("contacts.json", "w") as f:
                json.dump(contacts, f, indent=4)
            return True
        except Exception:
            return False