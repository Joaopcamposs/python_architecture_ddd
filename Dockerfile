FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install --yes --force-yes python3-lxml python3-dev gcc

COPY requirements.txt /tmp/

RUN python -m pip install --upgrade pip

RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /src

COPY src/ /app/src/
RUN pip install -e /app/src
COPY tests/ /tests/

WORKDIR /src

EXPOSE 8001

CMD uvicorn --host 0.0.0.0 --port 8000 src.allocation.entrypoints.fast_api:app --workers 1 --log-level debug --forwarded-allow-ips="*" --proxy-headers