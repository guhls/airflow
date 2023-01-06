import datetime as dt

from airflow.models import DAG
from airflow.operators.python import PythonOperator

from tasks.common.funcs import extract_data, upload_data
from tasks.covid19_data_modeling.funcs import process_data

default_args = {
    'owner': 'admin',
    'start_date': dt.datetime(2023, 1, 1)
}

dag = DAG(
    dag_id='covid19_data_modeling',
    schedule_interval='@daily',
    default_args=default_args
)

extract_data_task = PythonOperator(
    task_id='extract_data_task',
    python_callable=extract_data,
    op_kwargs={"date": '2022-11-16'},
    dag=dag
)

process_data_task = PythonOperator(
    task_id='process_data_task',
    python_callable=process_data,
    dag=dag
)

upload_data_task = PythonOperator(
    task_id='upload_data_task',
    python_callable=upload_data,
    dag=dag
)

extract_data_task >> process_data_task >> upload_data_task
