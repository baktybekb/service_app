FROM python:3.11-alpine

RUN apk add --no-cache postgresql-client build-base postgresql-dev

COPY requirements.txt /temp/requirements.txt
RUN pip install --no-cache-dir -r /temp/requirements.txt

COPY service /service
WORKDIR /service

RUN adduser --disabled-password service-user
USER service-user

EXPOSE 8000

