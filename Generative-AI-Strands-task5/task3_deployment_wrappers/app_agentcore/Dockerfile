FROM python:3.12-slim

WORKDIR /app

RUN useradd -m -u 1000 appuser

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER appuser
EXPOSE 8080

CMD ["python", "app.py"]