FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir pipenv && \
    pipenv requirements > requirements.txt && \
    pip install -r requirements.txt && \
    pip install gunicorn