FROM python:3.8.0

WORKDIR /app

COPY . /app

RUN apt-get update
RUN apt install -y libgl1-mesa-glx
RUN pip install -r app/requirements.txt

EXPOSE 8081
#CMD ["python","-m", "app.initialize_db"]

#CMD ["flask", "run", "--host=0.0.0.0", "--port=8081"]

CMD ["uwsgi", "app.ini"]

