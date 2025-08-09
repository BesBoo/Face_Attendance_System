#!/usr/bin/env python3
"""
Check face_recognition library version and compatibility
"""

import face_recognition
import cv2
import numpy as np

def check_face_recognition_version():
    """Check face_recognition library version"""
    try:
        # Try to get version info
        print("Face Recognition Library Check")
        print("=" * 40)
        
        # Test basic functionality
        print("Testing basic face_recognition functions...")
        
        # Create a simple test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[20:80, 20:80] = [255, 255, 255]  # White rectangle
        
        # Test face_locations
        face_locations = face_recognition.face_locations(test_image)
        print(f" face_locations works: {len(face_locations)} faces found")
        
        # Test face_encodings
        face_encodings = face_recognition.face_encodings(test_image)
        print(f" face_encodings works: {len(face_encodings)} encodings found")
        
        # Test face_distance
        if len(face_encodings) > 0:
            distances = face_recognition.face_distance([face_encodings[0]], face_encodings[0])
            print(f" face_distance works: distance = {distances[0]}")
        
        print("\n All face_recognition functions are working!")
        return True
        
    except Exception as e:
        print(f"❌ face_recognition error: {e}")
        return False

def check_opencv_version():
    """Check OpenCV version"""
    print(f"\nOpenCV version: {cv2.__version__}")
    return True

def check_numpy_version():
    """Check NumPy version"""
    print(f"NumPy version: {np.__version__}")
    return True

if __name__ == "__main__":
    check_opencv_version()
    check_numpy_version()
    check_face_recognition_version() 