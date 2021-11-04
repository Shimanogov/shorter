FROM python:3
COPY backend.py .
COPY web-page.html .
COPY oops.html .
COPY requirements.txt .
COPY favicon.ico .

RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0"]