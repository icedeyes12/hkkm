"""
Voice Chat Module
Provides speech-to-text and text-to-speech functionality
"""

import os
import sys
from typing import Optional, Dict, Any

# Check if voice dependencies are available
VOICE_AVAILABLE = True
try:
    import speech_recognition as sr
    import pyttsx3
except ImportError:
    VOICE_AVAILABLE = False


class VoiceChat:
    """Voice chat handler for speech recognition and synthesis"""
    
    def __init__(self):
        self.recognizer = None
        self.tts_engine = None
        self.is_initialized = False
        
        if VOICE_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.tts_engine = pyttsx3.init()
                self._configure_tts()
                self.is_initialized = True
            except Exception as e:
                print(f"⚠️ Voice initialization failed: {e}")
                self.is_initialized = False
        else:
            print("⚠️ Voice dependencies not installed. Voice features disabled.")
    
    def _configure_tts(self):
        """Configure text-to-speech engine"""
        if self.tts_engine:
            try:
                # Set properties
                self.tts_engine.setProperty('rate', 150)  # Speed
                self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
                
                # Try to set a pleasant voice
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Prefer female voice if available
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
            except Exception as e:
                print(f"⚠️ TTS configuration warning: {e}")
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Dict[str, Any]:
        """
        Listen for voice input and convert to text
        
        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for the phrase
            
        Returns:
            Dict with success status and transcribed text or error
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "Voice recognition not available. Please install dependencies."
            }
        
        try:
            with sr.Microphone() as source:
                print("🎤 Listening... (speak now)")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                print("🔄 Processing speech...")
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                
                return {
                    "success": True,
                    "text": text
                }
                
        except sr.WaitTimeoutError:
            return {
                "success": False,
                "error": "No speech detected. Please try again."
            }
        except sr.UnknownValueError:
            return {
                "success": False,
                "error": "Could not understand audio. Please speak clearly."
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "error": f"Speech recognition service error: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def speak(self, text: str) -> Dict[str, Any]:
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
            
        Returns:
            Dict with success status
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "Text-to-speech not available. Please install dependencies."
            }
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            return {
                "success": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"TTS Error: {str(e)}"
            }
    
    def is_available(self) -> bool:
        """Check if voice features are available"""
        return self.is_initialized
    
    def get_microphone_list(self) -> list:
        """Get list of available microphones"""
        if not VOICE_AVAILABLE:
            return []
        
        try:
            return sr.Microphone.list_microphone_names()
        except Exception:
            return []


class VoiceCommandParser:
    """Parse voice commands for special actions"""
    
    WAKE_WORDS = ["hey assistant", "hello assistant", "hi assistant"]
    STOP_WORDS = ["stop", "exit", "quit", "goodbye"]
    
    @staticmethod
    def is_wake_word(text: str) -> bool:
        """Check if text contains a wake word"""
        text_lower = text.lower().strip()
        return any(wake in text_lower for wake in VoiceCommandParser.WAKE_WORDS)
    
    @staticmethod
    def is_stop_word(text: str) -> bool:
        """Check if text contains a stop word"""
        text_lower = text.lower().strip()
        return any(stop in text_lower for stop in VoiceCommandParser.STOP_WORDS)
    
    @staticmethod
    def extract_command(text: str) -> Optional[str]:
        """Extract command from voice input"""
        text_lower = text.lower().strip()
        
        # Remove wake words
        for wake in VoiceCommandParser.WAKE_WORDS:
            if wake in text_lower:
                text_lower = text_lower.replace(wake, "").strip()
        
        return text_lower if text_lower else None


# Singleton instance
_voice_chat_instance = None


def get_voice_chat() -> VoiceChat:
    """Get or create voice chat singleton instance"""
    global _voice_chat_instance
    if _voice_chat_instance is None:
        _voice_chat_instance = VoiceChat()
    return _voice_chat_instance
