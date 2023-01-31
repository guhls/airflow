# Imports
import datetime as dt
import os

import pandas.errors
import requests
from pathlib import Path

import pandas as pd
import pyathena
from pyathena.pandas.cursor import PandasCursor
from airflow.models import DAG # noqa
from airflow.operators.python import PythonOperator # noqa
from dotenv import load_dotenv
from googleapiclient.discovery import build
import psycopg2
import sqlite3

from auth.google.creds import get_creds

load_dotenv()

S3_COVID_EXTRACT = os.environ.get("S3_COVID_EXTRACT")
POSTGRES_ENV = {
    'host': os.environ.get("host"),
    'database': os.environ.get("database"),
    'user': os.environ.get("user"),
    'password': os.environ.get("password"),
    'connect_timeout': int(os.environ.get("connect_timeout"))
}

path_root = Path(__file__).parent.parent

# Functions


def get_data_from_athena(query_athena, s3_staging_dir):
    conn = pyathena.connect(
        s3_staging_dir=s3_staging_dir,
        region_name=os.environ.get("REGION_NAME"),
        cursor_class=PandasCursor
    )

    with conn.cursor() as cur:
        df = cur.execute(query_athena).as_pandas()

    return df


def get_df_from_ids(ids):
    lst_dfs = []
    for cnes_id in ids:
        uri = f"https://apidadosabertos.saude.gov.br/cnes/estabelecimentos/{cnes_id}"
        resp_data = requests.get(uri).json()

        df = pd.json_normalize(resp_data)
        lst_dfs.append(df)

    df_final = pd.concat(lst_dfs).reset_index(drop=True)
    return df_final


# TODO: Fazer com que popule com todos os dados do dataframe
def populate_cnes_info(df, conn):
    df\
        .sort_values(by='cnes_id')\
        .to_sql('cnes_info', conn, index=False, if_exists="append")


def rename_cnes_df(df):
    columns_to_rename = {
        'codigo_cnes': 'cnes_id',
        'nome_razao_social': 'nome_razao_social',
        'nome_fantasia': 'nome_fantasia',
        'codigo_cep_estabelecimento': 'cep_estabelecimento',
        'endereco_estabelecimento': 'endereco_estabelecimento',
        'numero_estabelecimento': 'numero_estabelecimento',
        'bairro_estabelecimento': 'bairro_estabelecimento',
        'latitude_estabelecimento_decimo_grau': 'latitude_estabelecimento',
        'longitude_estabelecimento_decimo_grau': 'longitude_estabelecimento'
    }

    columns = list(columns_to_rename.values())
    return df.rename(columns_to_rename, axis=1)[columns[:2] + columns[3:]]


def get_data_from_cnes(cnes_ids):
    try:
        conn = psycopg2.connect(**POSTGRES_ENV)
    except psycopg2.OperationalError as e:
        print(f"Connection with database PostgreSQL expire: {e}, creating conn with local db in sqlite...")

        conn = sqlite3.connect(f"{path_root}/db_local.db")

        print("Connected with Sqlite Database")

    query_cnes = f"""SELECT *
                FROM cnes_info
                WHERE codigo_cnes IN {str(set(cnes_ids))
                    .replace("{", "(")
                    .replace("}", ")")}
            """

    with conn:
        try:
            cnes_df = pd.read_sql_query(query_cnes, conn)
            if not cnes_df.empty:
                cnes_df_ids = cnes_df['codigo_cnes'].values.tolist()

                ids_to_add = set(cnes_ids) - set(cnes_df_ids)
                if ids_to_add:
                    df = get_df_from_ids(ids_to_add)
                    df = rename_cnes_df(df)
                    populate_cnes_info(df, conn)
                else:
                    return cnes_df
            else:
                df = get_df_from_ids(cnes_ids)
                df = rename_cnes_df(df)
                return df

            return pd.concat([cnes_df, df]).reset_index(drop=True)

        # pandas.errors.DatabaseError: Table not exists
        except pandas.errors.DatabaseError:
            df = get_df_from_ids(cnes_ids)
            df = rename_cnes_df(df)
            populate_cnes_info(df, conn)

            return df

# Tasks functions


def extract_data(**kwargs):
    query_athena = str(kwargs["query"])

    df = get_data_from_athena(query_athena, S3_COVID_EXTRACT)

    return df.to_json(orient="columns", date_format="iso")


# TODO: Alterar os valores da coluna vacina_data para o formato da data %Y-%m-%d
def process_data(**kwargs):
    data = kwargs["task_instance"].xcom_pull(task_ids="extract_data_task")
    df = pd.read_json(data)

    cnes_code = df['cnes_id'].values.tolist()
    cnes_df = get_data_from_cnes(cnes_code)

    df = df.merge(cnes_df, how='inner', on='cnes_id')
    df['vacina_dataaplicacao'] = df['vacina_dataaplicacao']\
        .apply(lambda date: dt.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.000").date()).astype(str)

    return df.to_json(orient="columns", date_format="iso")


def upload_data(**kwargs):
    data = kwargs["task_instance"].xcom_pull(task_ids="process_data_task")
    sheets_id = str(kwargs["sheet_id"])
    range_sheet = str(kwargs["range"])

    df = pd.read_json(data)

    service_sheets = build("sheets", "v4", credentials=get_creds())

    sheet = service_sheets.spreadsheets()

    values = [list(df)] + df.values.tolist()[0:]

    sheet.values().clear(spreadsheetId=sheets_id, range=range_sheet).execute()

    result = (  # noqa
        sheet.values()
        .update(
            spreadsheetId=sheets_id,
            range=range_sheet,
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
        WHERE "vacina_dataaplicacao" = date('2023-01-20')
        ORDER BY "cnes_id" DESC
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
range_ = "covid19!A1:V"

upload_data_task = PythonOperator(
    task_id="upload_data_task",
    python_callable=upload_data,
    op_kwargs={"sheet_id": sheet_id, "range": range_},
    dag=dag,
)

extract_data_task >> process_data_task >> upload_data_task


if __name__ == "__main__":
    get_data_from_cnes([124, 9997423, 429031, 429023, 35])
