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


query = """
        SELECT *
        FROM "final"."covid19_vac_sp_view"
        WHERE "vacina_dataaplicacao" = date('2022-11-15')
        LIMIT 20
    """

extract_data_task = PythonOperator(
    task_id='extract_data_task',
    python_callable=extract_data,
    op_kwargs={"query": query},
    dag=dag
)

process_data_task = PythonOperator(
    task_id='process_data_task',
    python_callable=process_data,
    dag=dag
)


sheet_id = "1g7PgVQqFSXcZhySLQahgA0Cz9AvMFVN71RF3F7z1SRk"
range_ = "covid19!A1"

upload_data_task = PythonOperator(
    task_id='upload_data_task',
    python_callable=upload_data,
    op_kwargs={"sheet_id": sheet_id, "range": range_},
    dag=dag
)

extract_data_task >> process_data_task >> upload_data_task
