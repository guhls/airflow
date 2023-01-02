FROM apache/airflow:2.5.0
COPY .env .
RUN pip install pyathena pandas