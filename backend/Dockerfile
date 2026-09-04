FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements/main.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./

EXPOSE 8000

CMD ["uvicorn", "main:create_app", "--host", "0.0.0.0", "--port", "8000"]
