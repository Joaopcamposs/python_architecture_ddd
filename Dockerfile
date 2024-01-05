FROM python:3.11-slim-bullseye

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

COPY requirements.txt /tmp/

RUN python -m pip install --upgrade pip

RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /src

COPY src/ /src/
RUN pip install -e /src
COPY tests/ /tests/

WORKDIR /
