FROM python:3.12-slim

WORKDIR /srv
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .

RUN useradd --uid 10001 --no-create-home docshare
USER 10001

ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
