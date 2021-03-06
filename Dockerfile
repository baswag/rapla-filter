FROM python:3.7-alpine as base
FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt
RUN pip install --ignore-install --upgrade --prefix=/install -r /requirements.txt


FROM base as prod
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


FROM prod as debug

RUN pip install connexion[swagger-ui]
ENV APP_DEBUG 1
COPY src/entrypoint_debug.sh /app/entrypoint.sh