#!/usr/bin/env python3
"""
Audio Feedback System
Provides audio cues and text-to-speech feedback for voice commands
"""

import os
import platform
import threading
from enum import Enum
from logger_config import get_logger

logger = get_logger(__name__)


class AudioCue(Enum):
    """Predefined audio cue types"""
    LISTENING_START = "listening_start"
    LISTENING_STOP = "listening_stop"
    COMMAND_RECOGNIZED = "command_recognized"
    COMMAND_SUCCESS = "command_success"
    COMMAND_ERROR = "command_error"
    WARNING = "warning"


class AudioFeedbackManager:
    """
    Manages audio feedback for the voice command system
    Provides audio cues and optional text-to-speech
    """
    
    def __init__(self):
        self.system = platform.system()
        self.enabled = True
        self.tts_enabled = False
        self.tts_engine = None
        
        # Try to setup TTS
        self._setup_tts()
        
        logger.info(f"AudioFeedbackManager initialized for {self.system}")
    
    def _setup_tts(self):
        """Setup text-to-speech engine"""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS
            self.tts_engine.setProperty('rate', 150)  # Speed
            self.tts_engine.setProperty('volume', 0.8)  # Volume
            
            logger.info("TTS engine initialized successfully")
            
        except ImportError:
            logger.warning("pyttsx3 not installed - TTS unavailable")
            self.tts_engine = None
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None
    
    def play_beep(self, frequency=1000, duration=200):
        """
        Play a simple beep sound
        
        Args:
            frequency: Frequency in Hz (default: 1000)
            duration: Duration in milliseconds (default: 200)
        """
        if not self.enabled:
            return
        
        try:
            if self.system == "Windows":
                import winsound
                winsound.Beep(frequency, duration)
            elif self.system == "Darwin":  # macOS
                os.system(f'afplay /System/Library/Sounds/Ping.aiff')
            elif self.system == "Linux":
                # Use paplay or aplay for system sounds
                os.system(f'paplay /usr/share/sounds/freedesktop/stereo/message.oga 2>/dev/null || '
                         f'aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null')
        except Exception as e:
            logger.error(f"Failed to play beep: {e}")
    
    def play_cue(self, cue_type):
        """
        Play a predefined audio cue
        
        Args:
            cue_type: AudioCue enum value
        """
        if not self.enabled:
            return
        
        # Map cue types to frequencies/patterns
        cue_patterns = {
            AudioCue.LISTENING_START: (800, 100),      # Low beep
            AudioCue.LISTENING_STOP: (600, 100),       # Lower beep
            AudioCue.COMMAND_RECOGNIZED: (1200, 150),  # Higher beep
            AudioCue.COMMAND_SUCCESS: (1400, 100),     # Success tone
            AudioCue.COMMAND_ERROR: (400, 300),        # Error tone
            AudioCue.WARNING: (1000, 200),             # Warning tone
        }
        
        if cue_type in cue_patterns:
            freq, duration = cue_patterns[cue_type]
            threading.Thread(
                target=self.play_beep,
                args=(freq, duration),
                daemon=True
            ).start()
    
    def speak(self, text, async_mode=True):
        """
        Speak text using TTS
        
        Args:
            text: Text to speak
            async_mode: If True, speak in background thread
        """
        if not self.enabled or not self.tts_enabled or not self.tts_engine:
            return
        
        def _speak():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS error: {e}")
        
        if async_mode:
            threading.Thread(target=_speak, daemon=True).start()
        else:
            _speak()
    
    # Convenience methods for common scenarios
    
    def listening_started(self):
        """Audio feedback for listening start"""
        self.play_cue(AudioCue.LISTENING_START)
        if self.tts_enabled:
            self.speak("Listening")
    
    def listening_stopped(self):
        """Audio feedback for listening stop"""
        self.play_cue(AudioCue.LISTENING_STOP)
    
    def command_recognized(self, command=None):
        """Audio feedback for command recognition"""
        self.play_cue(AudioCue.COMMAND_RECOGNIZED)
        if self.tts_enabled and command:
            self.speak(f"Recognized: {command[:30]}")
    
    def command_executed(self, success=True, message=None):
        """Audio feedback for command execution"""
        if success:
            self.play_cue(AudioCue.COMMAND_SUCCESS)
            if self.tts_enabled:
                self.speak(message or "Command executed successfully")
        else:
            self.play_cue(AudioCue.COMMAND_ERROR)
            if self.tts_enabled:
                self.speak(message or "Command failed")
    
    def warning(self, message=None):
        """Audio feedback for warnings"""
        self.play_cue(AudioCue.WARNING)
        if self.tts_enabled and message:
            self.speak(message)
    
    def enable_audio_cues(self):
        """Enable audio cues"""
        self.enabled = True
        logger.info("Audio cues enabled")
    
    def disable_audio_cues(self):
        """Disable audio cues"""
        self.enabled = False
        logger.info("Audio cues disabled")
    
    def enable_tts(self):
        """Enable text-to-speech"""
        if self.tts_engine:
            self.tts_enabled = True
            logger.info("TTS enabled")
            return True
        else:
            logger.warning("Cannot enable TTS - engine not available")
            return False
    
    def disable_tts(self):
        """Disable text-to-speech"""
        self.tts_enabled = False
        logger.info("TTS disabled")
    
    def toggle_audio_cues(self):
        """Toggle audio cues on/off"""
        self.enabled = not self.enabled
        status = "enabled" if self.enabled else "disabled"
        logger.info(f"Audio cues {status}")
        return self.enabled
    
    def toggle_tts(self):
        """Toggle TTS on/off"""
        if self.tts_engine:
            self.tts_enabled = not self.tts_enabled
            status = "enabled" if self.tts_enabled else "disabled"
            logger.info(f"TTS {status}")
            return self.tts_enabled
        return False
    
    def set_tts_rate(self, rate):
        """
        Set TTS speaking rate
        
        Args:
            rate: Words per minute (typically 100-300)
        """
        if self.tts_engine:
            try:
                self.tts_engine.setProperty('rate', rate)
                logger.info(f"TTS rate set to {rate}")
            except Exception as e:
                logger.error(f"Failed to set TTS rate: {e}")
    
    def set_tts_volume(self, volume):
        """
        Set TTS volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.tts_engine:
            try:
                volume = max(0.0, min(1.0, volume))  # Clamp to 0-1
                self.tts_engine.setProperty('volume', volume)
                logger.info(f"TTS volume set to {volume}")
            except Exception as e:
                logger.error(f"Failed to set TTS volume: {e}")
    
    def get_available_voices(self):
        """Get list of available TTS voices"""
        if self.tts_engine:
            try:
                voices = self.tts_engine.getProperty('voices')
                return [voice.name for voice in voices]
            except Exception as e:
                logger.error(f"Failed to get voices: {e}")
        return []
    
    def set_voice(self, voice_index=0):
        """
        Set TTS voice
        
        Args:
            voice_index: Index of voice to use
        """
        if self.tts_engine:
            try:
                voices = self.tts_engine.getProperty('voices')
                if 0 <= voice_index < len(voices):
                    self.tts_engine.setProperty('voice', voices[voice_index].id)
                    logger.info(f"TTS voice set to: {voices[voice_index].name}")
                else:
                    logger.warning(f"Invalid voice index: {voice_index}")
            except Exception as e:
                logger.error(f"Failed to set voice: {e}")


# Global audio feedback manager instance
_audio_manager = None


def get_audio_manager():
    """Get global audio feedback manager instance"""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioFeedbackManager()
    return _audio_manager


# Convenience functions

def play_listening_start():
    """Play listening start cue"""
    get_audio_manager().listening_started()


def play_listening_stop():
    """Play listening stop cue"""
    get_audio_manager().listening_stopped()


def play_command_recognized(command=None):
    """Play command recognized cue"""
    get_audio_manager().command_recognized(command)


def play_command_success(message=None):
    """Play command success cue"""
    get_audio_manager().command_executed(success=True, message=message)


def play_command_error(message=None):
    """Play command error cue"""
    get_audio_manager().command_executed(success=False, message=message)


def play_warning(message=None):
    """Play warning cue"""
    get_audio_manager().warning(message)


def speak_text(text, async_mode=True):
    """Speak text using TTS"""
    get_audio_manager().speak(text, async_mode)


if __name__ == "__main__":
    # Test audio feedback
    import time
    
    print("Testing audio feedback system...")
    
    am = get_audio_manager()
    
    print("\n1. Testing listening start...")
    am.listening_started()
    time.sleep(1)
    
    print("2. Testing command recognized...")
    am.command_recognized("open chrome")
    time.sleep(1)
    
    print("3. Testing command success...")
    am.command_executed(success=True)
    time.sleep(1)
    
    print("4. Testing command error...")
    am.command_executed(success=False)
    time.sleep(1)
    
    print("5. Testing listening stop...")
    am.listening_stopped()
    time.sleep(1)
    
    # Test TTS if available
    if am.tts_engine:
        print("\n6. Testing TTS...")
        print("Available voices:")
        for i, voice in enumerate(am.get_available_voices()):
            print(f"  {i}: {voice}")
        
        am.enable_tts()
        am.speak("Testing text to speech functionality", async_mode=False)
        print("TTS test complete")
    else:
        print("\nTTS not available (install pyttsx3)")
    
    print("\n✅ Audio feedback tests complete!")
