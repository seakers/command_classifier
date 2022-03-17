FROM python:3.7-slim-stretch

WORKDIR /app/command_classifier

COPY ./. /app/command_classifier

RUN pip3 install --no-cache-dir -r ./requirements.txt
RUN spacy download en
