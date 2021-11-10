import base64
import re
from hashlib import shake_128
from io import BytesIO

import coolname
import qrcode
import redis
import yaml
from fastapi import FastAPI, Request, Form
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

with open('config.yaml', 'r') as stream:
    config = yaml.safe_load(stream)

expiration_time = config['expiration_time']
bot_length = config['bot_length']
human_length = config['human_length']
collision_fix_times = config['collision_fix_times']
domain = config['domain']

app = FastAPI(title='Make your URL shorts')
templates = Jinja2Templates(directory=".")

main_db = redis.StrictRedis(host='redis', decode_responses=True, db=0)
redirection_db = redis.StrictRedis(host='redis', decode_responses=True, db=1)


@app.get("/", response_class=HTMLResponse)
async def base_render(request: Request):
    return templates.TemplateResponse("web-page.html", {"request": request,
                                                        'domain': domain})


@app.post("/", response_class=HTMLResponse)
async def result_render(request: Request, input_url: str = Form(...)):
    # check if user tries to shorten our link
    regexp = r'^https?:\/\/' + domain.replace(r'.', r'\.')
    if re.match(regexp, input_url):
        short = input_url.split('/')[-1]
        input_url = redirection_db.get(short)

    # check if url was already shorted
    values = main_db.hgetall(input_url)
    if values == {}:

        values = {  # generate new values
            'human': coolname.generate_slug(human_length),
            'bot': shake_128(input_url.encode('utf-8')).hexdigest(bot_length),
        }

        for _ in range(collision_fix_times):
            if redirection_db.get(values['bot']):  # check for collisions
                values['bot'] = shake_128((input_url + values['bot']).encode('utf-8')).hexdigest(bot_length)
            else:
                break

        for _ in range(collision_fix_times):
            if redirection_db.get(values['human']):  # check for collisions
                values['human'] = coolname.generate_slug(human_length)
            else:
                break

        main_db.hmset(input_url, values, )  # add new link
        redirection_db.mset({values['bot']: input_url, values['human']: input_url})  # make redirections

    main_db.expire(input_url, expiration_time)
    redirection_db.expire(values['bot'], expiration_time)
    redirection_db.expire(values['human'], expiration_time)

    # now make qr
    img = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    img.add_data('https://' + domain + '/' + values['bot'])
    img = img.make_image(image_factory=StyledPilImage,
                         module_drawer=RoundedModuleDrawer(),
                         embeded_image_path="/favicon.ico",
                         color_mask=SolidFillColorMask(back_color=(255, 255, 255)))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr = str(base64.b64encode(buffered.getvalue()))[2:-1]

    return templates.TemplateResponse("web-page.html", {'request': request,
                                                        'human': values['human'],
                                                        'bot': values['bot'],
                                                        'domain': domain,
                                                        'qr': qr})


@app.get('/favicon.ico', response_class=FileResponse)
async def favicon():
    return 'favicon.ico'


@app.get('/style.css', response_class=FileResponse)
async def css():
    return 'style.css'


@app.get("/{short}")
async def redirect(request: Request, short: str):
    long = redirection_db.get(short)

    if long:
        # now lets set up expirations:
        values = main_db.hgetall(long)
        main_db.expire(long, expiration_time)
        redirection_db.expire(values['bot'], expiration_time)
        redirection_db.expire(values['human'], expiration_time)

        return RedirectResponse(long)
    else:
        return templates.TemplateResponse('oops.html', {'request': request,
                                                        'domain': domain}, status_code=404)


@app.exception_handler(StarletteHTTPException)
async def my_custom_exception_handler(request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse('oops.html', {'request': request,
                                                        'domain': domain}, status_code=404)
    else:
        # Just use FastAPI's built-in handler for other errors
        return await http_exception_handler(request, exc)
