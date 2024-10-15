import os
import io
from google.cloud import vision
from googletrans import Translator
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")

def detect_text(image_path):
    """Detects text in an image using Google Vision API."""
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    
    if texts:
        return texts[0].description
    else:
        return None


# Example usage
# Replace '/mnt/data/handwritten.jpeg' with the actual image file path
