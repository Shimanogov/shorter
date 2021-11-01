from hashlib import shake_128

import coolname
import redis
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title='Make your URL shorts')
templates = Jinja2Templates(directory=".")

main_db = redis.StrictRedis(host='redis', decode_responses=True, db=0)
redirection_db = redis.StrictRedis(host='redis', decode_responses=True, db=1)


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("web-page.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def login(request: Request, input_url: str = Form(...)):
    values = main_db.hgetall(input_url)
    if values == {}:
        values = {
            'human': coolname.generate_slug(2),
            'bot': shake_128(input_url.encode('utf-8')).hexdigest(3),
        }
        main_db.hmset(input_url, values)
        redirection_db.mset({values['bot']: input_url, values['human']: input_url})
    return templates.TemplateResponse("web-page.html", {'request': request,
                                                        'human': values['human'],
                                                        'bot': values['bot'], })
    # TODO: pass name for webpage from docker compose
    # TODO: expiration time
    # TODO: check for collisions


@app.get('/favicon.ico', response_class=FileResponse)
async def favicon():
    return 'favicon.ico'


@app.get("/{short}", response_class=RedirectResponse)
async def read_item(short: str):
    long = redirection_db.get(short)
    return long
    # TODO: create oops fallback
    # TODO: make also work as shorter
    # TODO: reset expiration
