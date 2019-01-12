FROM python:3.6-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache curl python pkgconfig python-dev openssl-dev libffi-dev musl-dev make gcc

WORKDIR /app
COPY setup.py .
RUN pip install -e .
COPY ./templates ./templates
COPY ./ip_register_server.py .
COPY ./blockchain.py .



EXPOSE 5000
