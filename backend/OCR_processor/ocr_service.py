import json
import sys
from ocr_init import OCRManager


def initialize_ocr_service():
    """Initialize OCR service on startup (call once from backend)"""
    manager = OCRManager()
    result = manager.initialize()
    return result


if __name__ == "__main__":
    result = initialize_ocr_service()
    print(json.dumps(result))
