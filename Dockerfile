FROM python:3.12-slim

WORKDIR /project

COPY requirements.txt .

RUN pip install --upgrade pip

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install -r requirements.txt

COPY project .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]