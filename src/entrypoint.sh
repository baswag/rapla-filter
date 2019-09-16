#!/bin/sh

nginx
gunicorn -w2 Main:app.app