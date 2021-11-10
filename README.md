# shorter

Lightweight opensource webapp creating short urls.

Created as a student project in ~2 weeks during Autumn 2021 using FastAPI, Jinja2 and Redis.

Currently, autodeploys on https://shorter.fit

Website saves urls for two weeks since last usage of shorted link.

## project structure

### front

- web-page.html
- oops.html
- favicon.ico
- style.css

### back/api

- backend.py
- config.yaml
- requirements.txt

### deployment

- Dockerfile
- docker-compose.yaml

### db

Database consists of two redis db instances. Two instances path were chosen for speed of requests handling.

## self-deployment instructions

Currently, github action alex-ac/github-action-ssh-docker-compose is used to deploy on each release. Server also uses
nginx to establish ssl-secure connection. Nginx runs in non-container mode because of safe containing of ssl-key. To
deploy this yourself, clone, setup nginx on your server and setup all github secrets mentioned in worklows/main.yml e.g.
ssh key and user.