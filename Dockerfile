FROM python:3.5-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  git \
  gcc \
  libxml2-dev \
  libxslt1-dev \
  libz-dev \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY . /code/
RUN pip install -r requirements/dev.txt

ENTRYPOINT ["/code/docker/entrypoint"]

ENV DJANGO_SETTINGS_MODULE openstax.settings.docker

CMD docker/start
