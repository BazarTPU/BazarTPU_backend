FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir pip -r requirements.txt

COPY user_service/ ./user_service/

CMD ["uvicorn", "user_service.main:app", "--host", "0.0.0.0", "--port", "8002"]