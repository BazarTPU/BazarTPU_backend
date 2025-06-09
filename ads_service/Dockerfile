FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ads_service/ ./ads_service/

CMD ["uvicorn", "ads_service.main:app", "--host", "0.0.0.0", "--port", "8001"]