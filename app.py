import os
from fastapi import FastAPI, UploadFile, File
from groqModel import get_land_details, get_content, get_site_plan
from fastapi.responses import RedirectResponse
from convert_pdf import convert_pdf_to_jpg, merge_pdf
from shutil import rmtree
import json
from fastapi.middleware.cors import CORSMiddleware

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
    files_to_merge = [deedOfAssignment, landTitleCertificate, transferDocument]
    for file in files_to_merge:
        tmp_filepath = f'vlm/{file.filename}'
        with open(tmp_filepath, 'wb') as temp_file:
            content = await file.read()
            temp_file.write(content)

    merged_file = merge_pdf('vlm')
    name = 'user_docs' 
 
    output = convert_pdf_to_jpg(merged_file, name)
    print('output path: ', output)
    pdf_content = get_content(output)
    print(pdf_content, ": pdf content")

    res = get_land_details(pdf_content)

    tmp_filepath = f'vlm/{sitePlan.filename}'
    with open(tmp_filepath, 'wb') as temp_file:
        content = await file.read()
        temp_file.write(content)

    output = convert_pdf_to_jpg(tmp_filepath, name)
    print('output path: ', output)
    pdf_content = get_content(output)
    print(pdf_content, ": pdf content")
    site_plan = get_site_plan(pdf_content)    

    rmtree(output, ignore_errors=True)  # Recursively delete the output directory
    os.remove(tmp_filepath)  
    res = json.loads(json.dumps(res))
    
    return res, site_plan

@app.get("/")
async def root():
    return RedirectResponse(url = '/docs')