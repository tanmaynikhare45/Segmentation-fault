import logging
import speech_recognition as sr
from typing import Dict
import time
import os

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """Real voice processor that actually recognizes speech"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Optimized settings for better recognition
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        logger.info("Real VoiceProcessor initialized")
    
    def process_audio_file(self, audio_path: str) -> Dict[str, str]:
        """Actually process and recognize speech from audio"""
        try:
            start_time = time.time()
            
            # Validate audio file
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return self._empty_result()
            
            # Process audio file
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            logger.info(f"Processing audio file: {audio_path}")
            
            # Try recognition with multiple approaches
            recognized_text = None
            detected_language = "unknown"
            
            # Method 1: Try English (US)
            try:
                text = self.recognizer.recognize_google(audio, language='en-US')
                if text and len(text.strip()) > 0:
                    recognized_text = text.strip()
                    detected_language = "english"
                    logger.info(f"English recognition successful: '{recognized_text}'")
            except sr.UnknownValueError:
                logger.debug("English recognition: No speech detected")
            except sr.RequestError as e:
                logger.warning(f"English recognition API error: {e}")
            except Exception as e:
                logger.debug(f"English recognition failed: {e}")
            
            # Method 2: Try Hindi if English failed
            if not recognized_text:
                try:
                    text = self.recognizer.recognize_google(audio, language='hi-IN')
                    if text and len(text.strip()) > 0:
                        recognized_text = text.strip()
                        detected_language = "hindi"
                        logger.info(f"Hindi recognition successful: '{recognized_text}'")
                except sr.UnknownValueError:
                    logger.debug("Hindi recognition: No speech detected")
                except sr.RequestError as e:
                    logger.warning(f"Hindi recognition API error: {e}")
                except Exception as e:
                    logger.debug(f"Hindi recognition failed: {e}")
            
            # Method 3: Try default Google recognition
            if not recognized_text:
                try:
                    text = self.recognizer.recognize_google(audio)
                    if text and len(text.strip()) > 0:
                        recognized_text = text.strip()
                        detected_language = "english"
                        logger.info(f"Default recognition successful: '{recognized_text}'")
                except sr.UnknownValueError:
                    logger.debug("Default recognition: No speech detected")
                except sr.RequestError as e:
                    logger.warning(f"Default recognition API error: {e}")
                except Exception as e:
                    logger.debug(f"Default recognition failed: {e}")
            
            processing_time = time.time() - start_time
            
            if recognized_text:
                return {
                    "original_text": recognized_text,
                    "detected_language": detected_language,
                    "english_text": recognized_text,
                    "confidence": 0.85,
                    "processing_time": processing_time
                }
            else:
                logger.warning("All recognition methods failed")
                return {
                    "original_text": "",
                    "detected_language": "unknown",
                    "english_text": "",
                    "confidence": 0.0,
                    "processing_time": processing_time
                }
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            return self._empty_result()
    
    def _empty_result(self) -> Dict[str, str]:
        """Return empty result"""
        return {
            "original_text": "",
            "detected_language": "unknown",
            "english_text": "",
            "confidence": 0.0,
            "processing_time": 0.0
        }
    
    def get_supported_languages(self):
        return ['english', 'hindi']