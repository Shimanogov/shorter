from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import redis
import coolname

app = FastAPI(title='Make your URL shorts')
templates = Jinja2Templates(directory="pages")

main_db = redis.StrictRedis(host='redis', decode_responses=True)


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.post("/")
async def login(input_url: str = Form(...)):
    short = coolname.generate_slug(3)
    main_db.set(short, input_url)
    return {"input_url": input_url, "short": short}


@app.get("/{short}", response_class=RedirectResponse)
async def read_item(short: str):
    long = main_db.get(short)
    return long
