FROM python:3.8.0

WORKDIR /app

COPY . /app

RUN apt-get update
RUN apt install -y libgl1-mesa-glx
RUN pip install -r app/requirements.txt

#RUN python -m app.initilize.initilize_db

CMD ["uwsgi", "app.ini"]

