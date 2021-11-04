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
    if values == {}:  # check if url already shorted

        values = {  # generate new values
            'human': coolname.generate_slug(2),
            'bot': shake_128(input_url.encode('utf-8')).hexdigest(3),
        }

        while redirection_db.get(values['bot']):  # check for collisions
            values['bot'] = shake_128((input_url+values['bot']).encode('utf-8')).hexdigest(3)

        while redirection_db.get(values['human']):  # check for collisions
            values['human'] = coolname.generate_slug(2)

        main_db.hmset(input_url, values, )  # add new link
        redirection_db.mset({values['bot']: input_url, values['human']: input_url})  # make redirections

    main_db.expire(input_url, 60 * 60 * 24 * 7 * 2)
    redirection_db.expire(values['bot'], 60 * 60 * 24 * 7 * 2)
    redirection_db.expire(values['human'], 60 * 60 * 24 * 7 * 2)

    return templates.TemplateResponse("web-page.html", {'request': request,
                                                        'human': values['human'],
                                                        'bot': values['bot'], })
    # TODO: pass name for webpage from docker compose


@app.get('/favicon.ico', response_class=FileResponse)
async def favicon():
    return 'favicon.ico'


@app.get("/{short}")
async def read_item(request: Request, short: str):
    long = redirection_db.get(short)

    if long:
        # now lets set up expirations:
        values = main_db.hgetall(long)
        main_db.expire(long, 60 * 60 * 24 * 7 * 2)
        redirection_db.expire(values['bot'], 60 * 60 * 24 * 7 * 2)
        redirection_db.expire(values['human'], 60 * 60 * 24 * 7 * 2)

        return RedirectResponse(long)
    else:
        return templates.TemplateResponse('oops.html', {'request': request})
    # TODO: make also work as shorter
