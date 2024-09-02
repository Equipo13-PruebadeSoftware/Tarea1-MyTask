FROM alpine:3.10

RUN apk add --no-cache python3-dev \
    && python3 -m ensurepip \
    && pip3 install --upgrade pip

WORKDIR /app

COPY . /app/

RUN pip3 --no-cache-dir install -r requirements.txt

CMD [ "python3", "src/main.py" ]