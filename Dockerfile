FROM python:3.6-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache curl python pkgconfig python-dev openssl-dev libffi-dev musl-dev make gcc

WORKDIR /app
COPY . /app
RUN pip install -e .

EXPOSE 5000
