# shorter

Lightweight opensource webapp creating short urls.

Created as a student project in ~2 weeks during Autumn 2021 using FastAPI, Jinja2 and Redis.

Currently, autodeploys on http://shorter.fit

Website saves urls for two weeks since last usage of shorted link.

## project structure

### front

- web-page.html renders all responses with help of jinja templates
- oops.html works as a broken links handler
- favicon.ico

### back/api

- backend.py contains fastapi instructions for uvicorn connected with redis client

### deployment

- Dockerfile contains docker with back/api
- docker-compose.yaml runs dockerfile and redis db container

## self-deployment instructions

To be done...