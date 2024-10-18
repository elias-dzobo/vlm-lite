import os
from fastapi import FastAPI, UploadFile, File
from groqModel import get_land_details, get_content, get_site_plan
from fastapi.responses import RedirectResponse
from convert_pdf import convert_pdf_to_jpg, merge_pdf, parse_json
from concurrent.futures import ProcessPoolExecutor
import asyncio
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

async def cleanup(temp_files, output_dir):
    try:
        for file in temp_files:
            os.remove(file)
        rmtree(output_dir, ignore_errors=True)
    except Exception as e:
        print(f"Error during cleanup: {e}")

@app.post("/process_pdf/")
async def process_pdf(
    deedOfAssignment: UploadFile = File(...),
    landTitleCertificate: UploadFile = File(...),
    transferDocument: UploadFile = File(...),
    sitePlan: UploadFile = File(...)
):
    print('started')
    temp_dir = 'temp_docs'
    os.makedirs(temp_dir, exist_ok=True)
    tmp_filepaths = []
    
    try:
        # Save the uploaded files asynchronously
        files_to_merge = [deedOfAssignment, landTitleCertificate, transferDocument, sitePlan]
        for file in files_to_merge:
            tmp_filepath = f'{temp_dir}/{file.filename}'
            tmp_filepaths.append(tmp_filepath)

            async with aiofiles.open(tmp_filepath, 'wb') as temp_file:
                while content := await file.read(1024 * 1024):  # 1 MB chunks
                    await temp_file.write(content)

        # Offload CPU-bound tasks to a thread pool
        with ProcessPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            merged_file = await loop.run_in_executor(executor, merge_pdf, temp_dir)
            name = 'user_docs'
            output = await loop.run_in_executor(executor, convert_pdf_to_jpg, merged_file, name)

        # Extract content
        pdf_content = get_content(output)
        res = get_land_details(pdf_content)

        # Schedule cleanup in the background 
        await asyncio.create_task(cleanup(tmp_filepaths, output))

        
        json_response = parse_json(res)

        print(type(json_response))
        print(json_response)

        return json_response

    except Exception as e:
        print(f"Error processing PDF: {e}")
        await asyncio.create_task(cleanup(tmp_filepaths, output))
        raise e


@app.get("/")
async def root():
    return RedirectResponse(url = '/docs')