"""OpenAI assistant for understanding email intent from voice commands."""

import json
from openai import OpenAI

class EmailAssistant:
    def __init__(self, api_key):
        """Initialize the OpenAI email assistant.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
    
    def analyze_command(self, command, conversation_context=""):
        """Analyze a voice command and determine the user's intent.
        
        Args:
            command: The voice command text to analyze
            conversation_context: Optional context from previous interactions
            
        Returns:
            Dict containing the intent analysis or None on error
        """
        # Set up the prompt for OpenAI
        analysis_prompt = f"""You are an intelligent email assistant helping a user compose emails by voice.
        
{conversation_context}The user just said: "{command}"

Based on this and any previous context:
1) What is the user trying to do? (INTENT)
2) If they're composing an email, extract any recipient, subject, or message content
3) If they're continuing a previous thought, merge it with existing context

Return your analysis as a clean JSON object with this format - don't include anything else in your response:
{{
  "intent": "COMPOSE_EMAIL or SEND_EMAIL or ADD_CONTACT or CLEAR_FORM or CONTINUE_BODY or HELP or UNKNOWN",
  "recipient": "name or email or null if not specified",
  "subject": "subject text or null if not specified",
  "body": "email body content or null if not specified",
  "continue_previous": true/false,
  "explanation": "brief explanation of what you understood"
}}"""

        try:
            # Ask OpenAI to understand the command
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse the JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Return None if we couldn't parse the response
                return None
            
        except Exception:
            # Return None on any error
            return None