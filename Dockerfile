FROM python:3.7-alpine as base
FROM base as builder

RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt

RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base
COPY --from=builder /install /usr/local

RUN apk add --update --no-cache nginx

ENV APP_DEBUG 0

COPY docker-nginx.conf /etc/nginx/nginx.conf
COPY docker-nginx-proxy.conf /etc/nginx/conf.d/default.conf
RUN mkdir -p /run/nginx

COPY src /app
RUN chmod -R 777 /app/static/
WORKDIR /app

EXPOSE 5000
CMD ["./entrypoint.sh"]
