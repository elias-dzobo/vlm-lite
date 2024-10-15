import os
from fastapi import FastAPI, UploadFile, File
from groqModel import get_land_details, get_content, get_site_plan
from fastapi.responses import RedirectResponse
from convert_pdf import convert_pdf_to_jpg, merge_pdf
from shutil import rmtree
import json
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
import json

app = FastAPI()

origins = ['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_pdf/")
async def process_pdf(
    deedOfAssignment: UploadFile = File(...),
    landTitleCertificate: UploadFile = File(...),
    transferDocument: UploadFile = File(...),
    sitePlan: UploadFile = File(...)
):
    temp_dir = 'temp_docs'
    os.makedirs(temp_dir, exist_ok=True)
    tmp_filepaths = []
    
    try:
        # Save the uploaded files temporarily
        files_to_merge = [deedOfAssignment, landTitleCertificate, transferDocument, sitePlan]
        for file in files_to_merge:
            tmp_filepath = f'{temp_dir}/{file.filename}'
            tmp_filepaths.append(tmp_filepath)

            # Asynchronously write the file to disk
            async with aiofiles.open(tmp_filepath, 'wb') as temp_file:
                content = await file.read()
                await temp_file.write(content)

        # Merge the PDFs
        merged_file = merge_pdf(temp_dir)
        name = 'user_docs'

        # Convert merged PDF to JPG
        output = convert_pdf_to_jpg(merged_file, name)
        print('output path: ', output)

        # Extract content from the converted JPG
        pdf_content = get_content(output)
        print(pdf_content, ": pdf content")

        # Get land details based on the extracted content
        res = get_land_details(pdf_content)

        # Clean up output and temporary files
        rmtree(output, ignore_errors=True)  # Recursively delete the output directory
        for tmp_filepath in tmp_filepaths:
            os.remove(tmp_filepath)  # Remove all temporary files

        res = json.loads(json.dumps(res))
        return res

    except Exception as e:
        print(f"Error processing PDF: {e}")
        # Clean up even in case of an error
        rmtree(output, ignore_errors=True)
        for tmp_filepath in tmp_filepaths:
            if os.path.exists(tmp_filepath):
                os.remove(tmp_filepath)
        raise e

@app.get("/")
async def root():
    return RedirectResponse(url = '/docs')