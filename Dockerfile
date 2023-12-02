FROM python:3.11-slim-bullseye

COPY requirements.txt /tmp

RUN python -m pip install --upgrade pip

RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /code

COPY *.py /code/

WORKDIR /code

EXPOSE 8000

#CMD flask run --host=0.0.0.0 --port=80
CMD uvicorn --host 0.0.0.0 --port 8000 src.allocation.entrypoints.fast_api:app --workers 1 --log-level debug --forwarded-allow-ips="*" --proxy-headers