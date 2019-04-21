FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get -y install git
RUN apt-get -y install gcc
RUN apt-get -y install libxml2-dev libxslt1-dev libz-dev

RUN mkdir /code

WORKDIR /code

COPY . /code/
RUN pip install -r requirements/dev.txt

ENTRYPOINT ["/code/docker/entrypoint"]

ENV DJANGO_SETTINGS_MODULE openstax.settings.docker

CMD docker/start
