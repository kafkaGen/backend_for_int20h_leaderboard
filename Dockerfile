FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN  openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/C=UA/ST=Kyiv/L=Kyiv/O=Best/OU=Best Kyiv/CN=best-kyiv.com"

EXPOSE 5000
