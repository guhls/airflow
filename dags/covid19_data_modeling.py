from airflow.models import DAG
from airflow.operators.python import PythonOperator
import datetime as dt
import funcs
import auth
import pandas as pd
from googleapiclient.discovery import build


def extract_data(*args, **kwargs):
    date = str(kwargs['date'])

    query = f"""
        SELECT * 
        FROM "final"."covid19_vac_sp_view" 
        WHERE "vacina_dataaplicacao" = date('{date}')
        LIMIT 100
    """

    df = funcs.get_data(query)
    return df.to_json()

def process_data(*args, **kwargs):
    data = kwargs['task_instance'].xcom_pull(task_ids='extract_data_task')
    df = pd.read_json(data)
    # Data Transform
    ...
    return df.to_json()

def upload_data(*args, **kwargs):
    data = kwargs['task_instance'].xcom_pull(task_ids='process_data_task')
    df = pd.read_json(data)

    service_sheets = build('sheets', 'v4', credentials=auth.creds.get_creds())

    sheet = service_sheets.spreadsheets()
    sheet_id = '1g7PgVQqFSXcZhySLQahgA0Cz9AvMFVN71RF3F7z1SRk'  # noqa
    range_ = 'covid19!A1'

    values = df.values.tolist()

    result = sheet.values().update(
        spreadsheetId=sheet_id,
        range=range_,
        valueInputOption='RAW',
        body={"values": values}
    ).execute()

default_args = {
    'owner': 'admin',
    'start_date': dt.datetime(2022,12,1)
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

if __name__ == '__main__':
   data = extract_data({'date': '2022-11-16'})
   process_data(data) 