# Imports
import datetime as dt
import os
import requests

import pandas as pd
import pyathena
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from dotenv import load_dotenv
from googleapiclient.discovery import build
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

from auth.google.creds import get_creds

load_dotenv()

# Functions


def get_data(query_athena):
    conn = pyathena.connect(
        s3_staging_dir=os.environ.get("S3_STAGING_DIR"),
        region_name=os.environ.get("REGION_NAME"),
    )

    return pd.read_sql_query(query_athena, conn)


def get_df_from_ids(ids):
    lst_dfs = []
    for id in ids:
        uri = f"https://apidadosabertos.saude.gov.br/cnes/estabelecimentos/{id}"
        resp_data = requests.get(uri).json()

        df = pd.json_normalize(resp_data)
        lst_dfs.append(df)

    df_final = pd.concat(lst_dfs).reset_index(drop=True)
    return df_final


def get_or_add_data(cnes_ids):
    engine = create_engine(
        "postgresql://postgres:681FtDgF8EoiwJ5alKIf@postegres-ec2.c6gbgu5unapw.us-east-2.rds.amazonaws.com/postgres_db"
    )

    query_cnes = f"""SELECT *
                FROM cnes_info
                WHERE codigo_cnes IN {str(set(cnes_ids))
                    .replace("{", "(")
                    .replace("}", ")")}
            """

    columns = ['codigo_cnes', 'nome_razao_social', 'nome_fantasia', 'codigo_cep_estabelecimento',
               'endereco_estabelecimento', 'numero_estabelecimento']

    with engine.connect() as conn:
        try:
            cnes_df = pd.read_sql_query(query_cnes, conn)
            if not cnes_df.empty:
                cnes_df_ids = cnes_df['codigo_cnes'].values.tolist()

                ids_to_add = set(cnes_ids) - set(cnes_df_ids)
                if ids_to_add:
                    df = get_df_from_ids(ids_to_add)
                    df[columns]\
                        .sort_values(by='codigo_cnes')\
                        .to_sql('cnes_info', conn, index=False, if_exists="append")
                else:
                    return cnes_df
            else:
                df = get_df_from_ids(cnes_ids)
                return df[columns]

            return pd.concat([cnes_df, df[columns]]).reset_index(drop=True)

        # ProgrammingError: psycopg2.errors.UndenfinedTable occurs when table not exists
        except ProgrammingError:
            df = get_df_from_ids(cnes_ids)
            df[columns]\
                .sort_values(by='codigo_cnes')\
                .to_sql('cnes_info', conn, index=False, if_exists="append")

            return df[columns]

# Tasks functions


def extract_data(*args, **kwargs):
    query = str(kwargs["query"])

    df = get_data(query)

    return df.to_json(orient="index", date_format="iso")


def process_data(*args, **kwargs):
    data = kwargs["task_instance"].xcom_pull(task_ids="extract_data_task")
    df = pd.read_json(data)

    # cnes_code = df['estabelecimento_valor'].values.tolist()

    return df.to_json(orient="index", date_format="iso")


def upload_data(*args, **kwargs):
    data = kwargs["task_instance"].xcom_pull(task_ids="process_data_task")
    sheet_id = str(kwargs["sheet_id"])
    range_ = str(kwargs["range"])

    df = pd.read_json(data)

    service_sheets = build("sheets", "v4", credentials=get_creds())

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

default_args = {"owner": "admin", "start_date": dt.datetime(2023, 1, 1)}

dag = DAG(
    dag_id="covid19_data_modeling",
    schedule_interval="@daily",
    default_args=default_args,
)


query = """
        SELECT *
        FROM "final"."covid19_vac_sp_view"
        WHERE "vacina_dataaplicacao" = date('2022-11-15')
        LIMIT 20
    """

extract_data_task = PythonOperator(
    task_id="extract_data_task",
    python_callable=extract_data,
    op_kwargs={"query": query},
    dag=dag,
)

process_data_task = PythonOperator(
    task_id="process_data_task", python_callable=process_data, dag=dag
)


sheet_id = "1g7PgVQqFSXcZhySLQahgA0Cz9AvMFVN71RF3F7z1SRk"
range_ = "covid19!A1"

upload_data_task = PythonOperator(
    task_id="upload_data_task",
    python_callable=upload_data,
    op_kwargs={"sheet_id": sheet_id, "range": range_},
    dag=dag,
)

extract_data_task >> process_data_task >> upload_data_task


if __name__ == "__main__":
    get_or_add_data([124, 9997423, 429031, 429023])
