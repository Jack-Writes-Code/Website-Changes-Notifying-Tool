FROM python:3.10.4-slim-buster

COPY requirements.txt /requirements.txt
RUN python -m pip install -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["python", "-u", "run.py"]