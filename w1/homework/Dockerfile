FROM python:3.9

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY ingest_data.py ingest_data.py
COPY green_taxi.csv.gz green_taxi.csv.gz
COPY zones_taxi.csv zones_taxi.csv

ENTRYPOINT ["python", "ingest_data.py"]
