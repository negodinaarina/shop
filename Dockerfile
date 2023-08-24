FROM python:3.9.7

COPY requirements.txt /

RUN pip3 install --upgrade pip

RUN pip3 install -r /requirements.txt



COPY . /main

WORKDIR /main



EXPOSE 8080



CMD ["gunicorn","--config", "gunicorn_config.py", "app:app"]