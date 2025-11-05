"""
AI Provider Handlers for Chatbot
Supports OpenRouter and Chutes AI platforms
"""

import requests
import json
from typing import Dict, List, Optional, Any


class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.conversation_history = []
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat message and get response"""
        raise NotImplementedError("Subclasses must implement chat method")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        raise NotImplementedError("Subclasses must implement get_available_models method")


class OpenRouterProvider(AIProvider):
    """OpenRouter AI Provider"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    AVAILABLE_MODELS = [
        "openai/gpt-4-turbo-preview",
        "openai/gpt-4",
        "openai/gpt-3.5-turbo",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-sonnet",
        "anthropic/claude-3-haiku",
        "meta-llama/llama-3-70b-instruct",
        "meta-llama/llama-3-8b-instruct",
        "google/gemini-pro",
        "mistralai/mistral-large",
        "mistralai/mistral-medium",
    ]
    
    def __init__(self, api_key: str, model: str = "openai/gpt-3.5-turbo"):
        super().__init__(api_key, model)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/hikikimo-life",
            "X-Title": "Hikikimo Life AI Assistant"
        }
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat message to OpenRouter"""
        try:
            # Build messages array
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history
            messages.extend(self.conversation_history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Make API request
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data["choices"][0]["message"]["content"]
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                # Keep only last 10 messages to manage context
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                return {
                    "success": True,
                    "message": assistant_message,
                    "model": self.model,
                    "provider": "OpenRouter"
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}",
                    "provider": "OpenRouter"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out. Please try again.",
                "provider": "OpenRouter"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}",
                "provider": "OpenRouter"
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenRouter models"""
        return self.AVAILABLE_MODELS


class ChutesProvider(AIProvider):
    """Chutes AI Provider"""
    
    BASE_URL = "https://api.chutes.ai/v1"
    
    AVAILABLE_MODELS = [
        "chutes-gpt-4",
        "chutes-gpt-3.5",
        "chutes-claude-3",
        "chutes-llama-3",
        "chutes-mistral",
    ]
    
    def __init__(self, api_key: str, model: str = "chutes-gpt-3.5"):
        super().__init__(api_key, model)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat message to Chutes"""
        try:
            # Build messages array
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history
            messages.extend(self.conversation_history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Make API request
            response = requests.post(
                f"{self.BASE_URL}/chat",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data.get("response", data.get("message", ""))
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                # Keep only last 10 messages to manage context
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                return {
                    "success": True,
                    "message": assistant_message,
                    "model": self.model,
                    "provider": "Chutes"
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}",
                    "provider": "Chutes"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out. Please try again.",
                "provider": "Chutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}",
                "provider": "Chutes"
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available Chutes models"""
        return self.AVAILABLE_MODELS


class AIProviderFactory:
    """Factory class to create AI providers"""
    
    @staticmethod
    def create_provider(provider_name: str, api_key: str, model: str) -> Optional[AIProvider]:
        """Create an AI provider instance"""
        provider_name = provider_name.lower()
        
        if provider_name == "openrouter":
            return OpenRouterProvider(api_key, model)
        elif provider_name == "chutes":
            return ChutesProvider(api_key, model)
        else:
            return None
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available providers"""
        return ["OpenRouter", "Chutes"]
