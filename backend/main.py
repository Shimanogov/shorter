from fastapi import FastAPI
from pydantic import BaseModel, Field


class InputURL(BaseModel):
    url: str = Field(..., title='Text', description='Input URL to be shorten', max_length=300)


app = FastAPI(title='Make your URL shorts')


@app.post("/add_url")
def add_url_to_database():
    pass

@app.get("/{short-url}")
def redirect():
    pass
