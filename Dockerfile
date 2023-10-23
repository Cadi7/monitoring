# pull official base image
FROM python:3.10

# set work directory
WORKDIR /code

# install dependencies
RUN pip install --upgrade pip && \
    pip install poetry && \
    pip install gunicorn==20.1.0

COPY ./poetry.lock /code/
COPY ./pyproject.toml /code/


RUN poetry config virtualenvs.create false
RUN poetry lock --no-update
RUN poetry install --no-interaction

COPY . /code/
COPY ./docker-startup.sh /code/
EXPOSE 8000

ENV DJANGO_ENV environment
ENV GUNICORN_BIND 0.0.0.0:8000
ENV GUNICORN_WORKERS 4
ENV GUNICORN_THREADS 4
ENV GUNICORN_WORKERS_CONNECTIONS 1001
ENV GUNICORN_TIMEOUT 300

CMD bash ./docker-startup.sh
