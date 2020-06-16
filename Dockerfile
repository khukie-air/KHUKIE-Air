FROM python:3.6.4
RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app/
RUN pip install -r requirements.txt && pip install gunicorn uwsgi
ADD . /app/