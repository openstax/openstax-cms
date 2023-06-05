FROM python:3.10-slim

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

WORKDIR /usr/local/cms-app

COPY ./requirements /usr/local/cms-app/requirements
COPY ./docker /usr/local/cms-app/docker
RUN pip install -r requirements/dev.txt

ENTRYPOINT ["/usr/local/cms-app/docker/entrypoint"]

ENV DJANGO_SETTINGS_MODULE openstax.settings.docker

CMD /usr/local/cms-app/docker/start
