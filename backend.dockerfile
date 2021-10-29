FROM python:3
WORKDIR /code
COPY ./backend .
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]