FROM python:3.7-alpine as base
FROM base as builder

RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt

RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base
COPY --from=builder /install /usr/local

ENV APP_DEBUG 0

COPY src /app
WORKDIR /app

EXPOSE 5000
CMD ["python", "Main.py"]
