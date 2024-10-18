import PyPDF2
from PyPDF2 import PdfFileMerger, PdfReader, PdfWriter
from pdf2image import convert_from_path
import os
import json

def merge_pdf(file_path):
    files = []

    for root, dirs, filenames in os.walk(file_path):
        for filename in filenames:
            if filename.endswith('.pdf'):
                files.append(os.path.join(root, filename))

    pdfWriter = PdfWriter()
    for file in files:
        pdfFileObj = open(file, 'rb')
        pdfReader = PdfReader(pdfFileObj)
        for pageNum in range(0, len(pdfReader.pages)):
            pageObj = pdfReader.pages[pageNum]
            pdfWriter.add_page(pageObj)

    pdfOutput = open('merged_files.pdf', 'wb')
    pdfWriter.write(pdfOutput)
    pdfOutput.close()
    
    return 'merged_files.pdf'


def convert_pdf_to_jpg(pdf_path, output_dir):
    """
    Converts all PDF files in the input directory to JPG images and saves them in the output directory.

    Args:
        input_dir (str): Path to the input directory containing PDF files.
        output_dir (str): Path to the output directory where converted JPG images will be saved.
    """
    base_path = 'vlm'

    if not os.path.exists(os.path.join(base_path, output_dir)):
    
        os.makedirs(os.path.join(base_path, output_dir))  # Create the output directory if it doesn't exist

    output_path = os.path.join(base_path, output_dir)

    try:
        images = convert_from_path(pdf_path)
        for i, img in enumerate(images):
            img_path = f'img_{i}.jpg' if i > 0 else 'img.jpg'  # Add index to output image path if multiple pages
            img.save(os.path.join(output_path, img_path), 'JPEG')

    except Exception as e:
        print(f'Error converting {pdf_path}: {e}')

    else:
        print(f'Successfully converted {pdf_path} to {output_path}')

    return output_path


def parse_json(json_string):
    json_string = json_string.replace("'", "") 
    json_content = json_string[json_string.find('{'):json_string.rfind('}') + 1]

    json_content = str(json_content).strip("'<>() ").replace('\'', '\"')

    

    print(type(json_content))

    data = json.loads(json_content)

    return data 

#convert_pdf_to_jpg('/Users/eliasdzobo/Downloads/Land Certificate .pdf', 'land_img')