FROM python:3.12-slim

WORKDIR /app

COPY ../ ./

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p output/text output/images

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]

