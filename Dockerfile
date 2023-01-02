FROM apache/airflow:2.5.0
COPY .env .

ENV PYTHONPATH /opt/airflow

RUN pip install pyathena pandas