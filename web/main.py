from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import redis
import coolname

app = FastAPI(title='Make your URL shorts')
templates = Jinja2Templates(directory="pages")

main_db = redis.Redis(host='redis')


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.post("/")
async def login(input_url: str = Form(...)):
    main_db.set(input_url, coolname.generate_slug())
    return {"input_url": input_url}
