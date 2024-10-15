from pdf2image import convert_from_path
from google_vision import detect_text
import os 
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain.output_parsers import StructuredOutputParser, ResponseSchema



img_dir = 'vlm/pdf_img'

response_schema = [
    ResponseSchema(
        name = 'Name of Owner/Title Holder',
        description = 'Answers the question who is the owner of the land'
    ),
    ResponseSchema(
        name = 'Legal Description of Property',
        description = 'Answers the question about the legal description of the land'
    ),
    ResponseSchema(
        name = 'Interest Held by Owner',
        description = 'Answers the question about the interest held by the owner'
    ),
    ResponseSchema(
        name = 'Term Held by Owner',
        description = 'Answers the question about the term held by the owner'
    ),
    ResponseSchema(
        name = 'Land Certificate Number',
        description = 'Answers the question about the certificate number of the land'
    ),
    ResponseSchema(
        name = 'Transfer Deed Number',
        description = 'Answers the question about the transfer deed number of the land'
    ),
    ResponseSchema(
        name = 'Name of Owners Grantor',
        description = 'Answers the question about the name of the grantor'
    ),
    ResponseSchema(
        name = 'Date of Transfer to Owner',
        description = 'Answers the question about the date of transfer to the owner'
    ),
    ResponseSchema(
        name = 'Date of issue of land certificate',
        description = 'Answers the question about the date the land certificate was issued'
    ),
    ResponseSchema(
        name = 'Date of Stamping of deed of transfer',
        description = 'Answers the question about the date the deed of transfer was stamped'
    ),
    ResponseSchema(
        name = 'Consent Data',
        description = 'Answers the question about the date of consent if consent was required'
    ),
    ResponseSchema(
        name = 'Barcode Title Plan',
        description = 'Returns the barcode title plan'
    ),
    ResponseSchema(
        name = 'Barcoded Site Plan',
        description = 'Returns the Barcoded site plan'
    ),
    ResponseSchema(
        name = 'Site Corrdinates',
        description = 'Returns the coordinates of every vertex of the property'
    )
]

output_parser = StructuredOutputParser.from_response_schemas(response_schema)

format_instructions = output_parser.get_format_instructions()


def get_content(img_dir):
    content = ''

    for image in os.listdir(img_dir):
        text = detect_text(os.path.join(img_dir, image))
        if text:
            content += (text + '\n')
        else:
            continue

    with open('content.txt', 'w') as f:
        f.write(content)

    return content


def get_land_details(content):
    prompt_template = """
                    Given the following information about the title deed to a land \n {title_deed}.
                    Answer the following questions 

                    1. What is the name of the owner of the land/title ?
                    2. What is the legal description of the property. This should include detailed description of the land, including plot size, boundaries, and geographic location ?
                    3. What is the interest held by the owner of the land ?
                    4. What is the term held by the land owner.
                    5. What is the land certificate number ?
                    6. What is the name of the Grantor ?
                    7. What is the date of transfer to the owner ?
                    8. What date was the land certificate issued ?
                    9. what date was the deed of transfer stamped ?
                    10. What is the consent data. if the consent date is not required answer with a blank space ?
                    11. What is the barcoded title plan ?
                    12. what is the barcoded site plan ?
                    13. what are the coordinates/bearings for every vertex of the property as perceived in a site plan ?

                    NOTE: ANSWER STRICTLY BASED IN INFORMATION FROM THE TITLE DEED PROVIDED. ALL DATES SHOULD BE IN THE FORMAT DAY/MONTH/YEAR 
                    DO NOT ANSWER IN A SENTENCE, INSTEAD RETURN THE ANSWER ONLY 

                    \n

                    {format_instructions}
                    
                    """

    prompt = PromptTemplate.from_template(
        template = prompt_template,
        partial_variables= {"format_instructions": format_instructions}
        )

    #chat_prompt = prompt.format(title_deed = content)

    llm = LLMChain(
        llm = ChatGroq(temperature=0, model='llama-3.1-70b-versatile'),
        prompt = prompt
    )

    res = llm.run(title_deed = content)
    
    return res 


def get_site_plan(content):
    prompt_template = """
                    Given the following information about the site plan of a land \n {site_plan}.
                    Answer the following questions 

                    1. what are the coordinates/bearings for every vertex of the property as perceived in a site plan ?

                    NOTE: ANSWER STRICTLY BASED IN INFORMATION FROM THE TITLE DEED PROVIDED. ALL DATES SHOULD BE IN THE FORMAT DAY/MONTH/YEAR 
                    DO NOT ANSWER IN A SENTENCE, INSTEAD RETURN THE ANSWER ONLY 

                    \n

                    {format_instructions}
                    
                    """

    prompt = PromptTemplate.from_template(
        template = prompt_template,
        partial_variables= {"format_instructions": format_instructions}
        )

    #chat_prompt = prompt.format(site_plan = content)

    llm = LLMChain(
        llm = ChatGroq(temperature=0, model='llama-3.1-70b-versatile'),
        prompt = prompt
    )

    res = llm.run(site_plan = content)
    
    return res 
