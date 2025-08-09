# face_recognition_modules/__init__.py

"""
Face Recognition Modules Package
Contains MediaPipe-based face recognition and fallback implementations
"""

try:
    from .mediapipe_recognizer import MediaPipeFaceRecognition
    MEDIAPIPE_AVAILABLE = True
except ImportError as e:
    MediaPipeFaceRecognition = None
    MEDIAPIPE_AVAILABLE = False
    print(f"MediaPipe face recognition not available: {e}")

try:
    from .recognizer import FaceRecognizer
    ORIGINAL_RECOGNIZER_AVAILABLE = True
except ImportError as e:
    FaceRecognizer = None
    ORIGINAL_RECOGNIZER_AVAILABLE = False
    print(f"Original face recognizer not available: {e}")

# Export available classes
__all__ = []

if MEDIAPIPE_AVAILABLE:
    __all__.append('MediaPipeFaceRecognition')

if ORIGINAL_RECOGNIZER_AVAILABLE:
    __all__.append('FaceRecognizer')

print(f"Face recognition modules loaded: {__all__}")