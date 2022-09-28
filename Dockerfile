FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir pipenv && \
    pipenv install && \
    pipenv install django-x-talk-template/. && \
    pipenv install gunicorn