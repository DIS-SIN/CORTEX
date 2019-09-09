FROM python:3.7-alpine

RUN apk add --no-cache bash bc \
    && pip3 install --upgrade pip \
    && pip3 install behave requests neo4j-driver

COPY . .

EXPOSE 8088

CMD behave
