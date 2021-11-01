FROM python:3
COPY backend.py .
COPY web-page.html .
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0"]