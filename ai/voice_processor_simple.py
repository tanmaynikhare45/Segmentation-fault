import logging
import speech_recognition as sr
from typing import Dict
import time

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """Simple voice processor that actually works"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        logger.info("Simple VoiceProcessor initialized")
    
    def process_audio_file(self, audio_path: str) -> Dict[str, str]:
        """Process audio file with basic recognition"""
        try:
            start_time = time.time()
            
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
            
            # Try simple English recognition first
            try:
                text = self.recognizer.recognize_google(audio, language='en-US')
                if text:
                    processing_time = time.time() - start_time
                    logger.info(f"Recognized: '{text}' in {processing_time:.2f}s")
                    return {
                        "original_text": text,
                        "detected_language": "english",
                        "english_text": text,
                        "confidence": 0.8,
                        "processing_time": processing_time
                    }
            except:
                pass
            
            # Try Hindi
            try:
                text = self.recognizer.recognize_google(audio, language='hi-IN')
                if text:
                    processing_time = time.time() - start_time
                    logger.info(f"Recognized Hindi: '{text}' in {processing_time:.2f}s")
                    return {
                        "original_text": text,
                        "detected_language": "hindi",
                        "english_text": text,
                        "confidence": 0.8,
                        "processing_time": processing_time
                    }
            except:
                pass
            
            # Default fallback
            try:
                text = self.recognizer.recognize_google(audio)
                if text:
                    processing_time = time.time() - start_time
                    logger.info(f"Fallback recognized: '{text}' in {processing_time:.2f}s")
                    return {
                        "original_text": text,
                        "detected_language": "unknown",
                        "english_text": text,
                        "confidence": 0.6,
                        "processing_time": processing_time
                    }
            except Exception as e:
                logger.error(f"All recognition failed: {e}")
            
            return self._empty_result()
            
        except Exception as e:
            logger.error(f"Voice processing failed: {e}")
            return self._empty_result()
    
    def _empty_result(self) -> Dict[str, str]:
        return {
            "original_text": "",
            "detected_language": "unknown",
            "english_text": "",
            "confidence": 0.0,
            "processing_time": 0.0
        }
    
    def get_supported_languages(self):
        return ['english', 'hindi']