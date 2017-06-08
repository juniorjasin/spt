FROM alpine:latest

RUN apk add --update py-pip
RUN apk add gcc openssl libc-dev python-dev
RUN pip install --upgrade pip
ADD . /usr/src/app
WORKDIR /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8081

CMD ["python", "/usr/src/app/app.py"]
