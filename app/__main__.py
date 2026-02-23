from typing import Annotated

import requests
from fastapi import APIRouter, Depends, FastAPI
from markitdown import MarkItDown
from openai import OpenAI
from pydantic import BaseModel, Field
from starlette.config import Config
from starlette.responses import PlainTextResponse

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
OPENAI_BASE_URL = config("OPENAI_BASE_URL", default=None)
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
DEFAULT_MODEL = config("DEFAULT_MODEL", default="gpt-4o")

openai = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)

app = FastAPI()
router = APIRouter(prefix="/v1")

def get_markItDown():
    session = requests.Session()
    session.headers.update(
        {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,pt-BR;q=0.8,pt-PT;q=0.7,pt;q=0.6",
            "cache-control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
        }
    )
    
    
    return MarkItDown(requests_session=session)

MarkItDownDep = Annotated["MarkItDown", Depends(get_markItDown)]

prompt = f"""
Your job is to clean transcripts of web pages coverted to markdown text.
The transcription tool includes all of the text content in the web page, your job is to clean it up and extract the relevant information in a well-formatted markdown.
If it's an article you want to start with `# Title` and then the text.
If it's a job description, you want to start with `# Job Title - Company` and then the text. You may also include the company description if it is present.
If it' some other type of page, you want to start with `# Title` and then the text.
The user will send the raw text in the next message. Then you will respond with the cleaned up text and nothing more.
"""

class ConvertRequest(BaseModel):
    uri: str = Field(examples=["https://openai.com"])
    model: str = Field(default=DEFAULT_MODEL)

@router.post("/convert")
async def transcribe(request: ConvertRequest, markitdown = Depends(get_markItDown)):
    result = markitdown.convert_uri(request.uri).markdown
    
    response = openai.responses.create( # noqa
        model=request.model,
        input=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": result,
            },
        ],
        stream=False,
    )
    
    text = ""
    for output in response.output:
        if output.type == "message" and output.role == "assistant":
            for content in output.content:
                text += content.text
    
    return PlainTextResponse(text)

app.include_router(router)
