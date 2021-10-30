from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field


class InputURL(BaseModel):
    url: str = Field(..., title='Text', description='Input URL to be shorten', max_length=300)


app = FastAPI(title='Make your URL shorts')
templates = Jinja2Templates(directory="pages")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})
