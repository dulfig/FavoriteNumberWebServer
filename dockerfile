FROM python:3.7.5

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 8432

CMD ["python3", "flaskApp.py"]
