# Imports
import datetime as dt
import os

import pandas as pd
import pyathena
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from dotenv import load_dotenv
from googleapiclient.discovery import build

from auth.google.creds import get_creds

load_dotenv()

# Functions


def get_data(query):
    conn = pyathena.connect(
        s3_staging_dir=os.environ.get('S3_STAGING_DIR'),
        region_name=os.environ.get('REGION_NAME')
        )

    return pd.read_sql_query(query, conn)


# Tasks functions

def extract_data(*args, **kwargs):
    query = str(kwargs["query"])

    df = get_data(query)

    return df.to_json(orient='index', date_format='iso')


def process_data(*args, **kwargs):
    data = kwargs['task_instance'].xcom_pull(task_ids='extract_data_task')
    df = pd.read_json(data)
    # Data Transform
    ...
    return df.to_json(orient='index', date_format='iso')


def upload_data(*args, **kwargs):
    data = kwargs["task_instance"].xcom_pull(task_ids="process_data_task")
    sheet_id = str(kwargs['sheet_id'])
    range_ = str(kwargs['range'])

    df = pd.read_json(data)

    service_sheets = build(
        "sheets", "v4", credentials=get_creds()
    )

    sheet = service_sheets.spreadsheets()

    values = [list(df)] + df.values.tolist()[0:]

    sheet.values().clear(spreadsheetId=sheet_id, range=range_)

    result = (  # noqa
        sheet.values()
        .update(
            spreadsheetId=sheet_id,
            range=range_,
            valueInputOption="RAW",
            body={"values": values},
        )
        .execute()
    )


# DAG

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
