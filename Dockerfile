FROM python:3.8.0

WORKDIR /app

COPY . /app

RUN apt-get update -y
RUN apt-get upgrade -y

RUN pip install -r requirements.txt


CMD ["python", "main.py"]
