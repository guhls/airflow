# Imports
import datetime as dt
from datetime import timedelta
import os
import boto3
import io

import requests
from pathlib import Path

import pandas as pd
import pyathena
from pyathena.pandas.util import as_pandas
from airflow.models import DAG # noqa
from airflow.operators.python import PythonOperator # noqa
from dotenv import load_dotenv
from googleapiclient.discovery import build

from auth.google.creds import get_creds

load_dotenv()

BUCKET = os.environ.get("S3_BUCKET")
REGION_NAME = os.environ.get("REGION_NAME")

FILE_PATH_UPLOAD = os.environ.get("FILE_PATH")
FILE_PATH_LACK_IDS = os.environ.get("FILE_PATH_LACK_IDS")

S3_STAGING_DIR = os.environ.get("S3_STAGING_DIR")

POSTGRES_ENV = {
    'host': os.environ.get("host"),
    'database': os.environ.get("database"),
    'user': os.environ.get("user"),
    'password': os.environ.get("password"),
    'connect_timeout': int(os.environ.get("connect_timeout"))
}

path_root = Path(__file__).parent.parent

# Functions


def get_data_from_athena(query_athena, as_df: bool = False):
    conn = pyathena.connect(
        s3_staging_dir=S3_STAGING_DIR,
        region_name=REGION_NAME
    )

    with conn.cursor() as cur:
        if as_df:
            cur.execute(query_athena)
            df = as_pandas(cur)

            return df

        result = cur.execute(query_athena).fetchall()

    return result


def send_df_to_s3(df_to_s3, bucket, file_path, query_recreate_parquet=None):
    if query_recreate_parquet:
        df_hf = get_data_from_athena(query_recreate_parquet, as_df=True)
        df_to_s3 = pd.concat([df_hf, df_to_s3], ignore_index=True).reset_index(drop=True)

    parquet_buffer = io.BytesIO()
    df_to_s3.to_parquet(parquet_buffer, engine="pyarrow", index=False)
    parquet_buffer.seek(0)

    s3 = boto3.client('s3')
    return s3.upload_fileobj(
        Fileobj=parquet_buffer,
        Bucket=bucket,
        Key=file_path
    )


def get_df_from_ids(ids):
    lst_dfs = []
    lst_ids_lack = []
    for cnes_id in ids:
        uri = f"https://apidadosabertos.saude.gov.br/cnes/estabelecimentos/{cnes_id}"
        resp_data = requests.get(uri).json()

        try:
            print(resp_data['codigo_cnes'])
        except KeyError:
            print(f"{cnes_id} not found")
            lst_ids_lack.append(cnes_id)
            continue

        df = pd.json_normalize(resp_data)

        lst_dfs.append(df)

    if lst_ids_lack:
        df_ids_lack = pd.DataFrame({"cnes_id": lst_ids_lack})

        query_lack_ids = "SELECT cnes_id FROM final.lack_cnes_id"
        send_df_to_s3(
            df_ids_lack,
            bucket=BUCKET,
            file_path=FILE_PATH_LACK_IDS,
            query_recreate_parquet=query_lack_ids
        )

    if lst_dfs:
        df_final = pd.concat(lst_dfs).reset_index(drop=True)
        return df_final

    return pd.DataFrame()


def rename_cnes_df(df):
    columns_to_rename = {
        'codigo_cnes': 'cnes_id',
        'nome_razao_social': 'nome_razao_social',
        'nome_fantasia': 'nome_fantasia',
        "codigo_uf": "codigo_uf",
        'codigo_cep_estabelecimento': 'cep_estabelecimento',
        'endereco_estabelecimento': 'endereco_estabelecimento',
        'numero_estabelecimento': 'numero_estabelecimento',
        'bairro_estabelecimento': 'bairro_estabelecimento',
        'latitude_estabelecimento_decimo_grau': 'latitude_estabelecimento',
        'longitude_estabelecimento_decimo_grau': 'longitude_estabelecimento'
    }

    columns = list(columns_to_rename.values())
    return df.rename(columns_to_rename, axis=1)[columns]


def update_healthcare_facilities(cnes_ids):
    query_cnes_geolocation = f"""
        SELECT DISTINCT cnes_id 
        FROM final.covid19_healthcare_facilities 
        WHERE cnes_id IN ({cnes_ids})
        """\
        .replace("[", "")\
        .replace("]", "")

    cnes_ids_hf = get_data_from_athena(query_cnes_geolocation.format(cnes_ids))
    cnes_ids_hf = [cnes_id[0] for cnes_id in cnes_ids_hf]

    ids_to_add = set(cnes_ids) - set(cnes_ids_hf)
    if ids_to_add:
        df_to_s3 = get_df_from_ids(ids_to_add)

        if df_to_s3.empty:
            print("Nothing to add")
            return

        df_to_s3 = rename_cnes_df(df_to_s3)

        query_recreate_parquet = "SELECT * FROM final.covid19_healthcare_facilities"
        send_df_to_s3(
            df_to_s3=df_to_s3,
            bucket=BUCKET,
            file_path=FILE_PATH_UPLOAD,
            query_recreate_parquet=query_recreate_parquet
        )


def send_df_to_sheets(df, sheets_id, range_sheet):
    service_sheets = build("sheets", "v4", credentials=get_creds())

    sheet = service_sheets.spreadsheets()

    df = df.fillna("")
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

    return result

# Tasks functions


def extract_data(**kwargs):
    query_athena = str(kwargs["query"])
    date = kwargs['execution_date']

    cnes_ids = get_data_from_athena(query_athena.format(date.strftime("%Y-%m-%d")))
    cnes_ids = [cnes_id[0] for cnes_id in cnes_ids]

    return cnes_ids


def process_data(**kwargs):
    cnes_ids = kwargs["task_instance"].xcom_pull(task_ids="extract_data_task")
    execution_date = kwargs["execution_date"]

    update_healthcare_facilities(cnes_ids)

    query_geolocation = f"""
        SELECT vacina_dataaplicacao, COUNT(*) total_vacinacoes
        FROM "final"."covid19_vac_sp_view" 
        WHERE "vacina_dataaplicacao" = date('{execution_date.strftime("%Y-%m-%d")}') AND 
        "cnes_id" NOT IN (SELECT "cnes_id" FROM "final"."lack_cnes_id")
        GROUP BY vacina_dataaplicacao
    """

    df = get_data_from_athena(query_geolocation, as_df=True)

    df['vacina_dataaplicacao'] = df['vacina_dataaplicacao'].astype(str)

    return df.to_json(orient="columns")


def upload_data(**kwargs):
    data = kwargs["task_instance"].xcom_pull(task_ids="process_data_task")
    sheets_id = str(kwargs["sheet_id"])
    range_sheet = str(kwargs["range"])

    df = pd.read_json(data)

    send_df_to_sheets(df, sheets_id, range_sheet)


# DAG

default_args = {
    "owner": "admin",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    "start_date": dt.datetime(2023, 1, 19),
    "end_date": dt.datetime(2023, 1, 25)
}

dag = DAG(
    dag_id="covid19_vac_by_CNES",
    schedule_interval="@daily",
    default_args=default_args,
)


query = """
        SELECT DISTINCT cnes_id
        FROM "final"."covid19_vac_sp_view"
        WHERE "vacina_dataaplicacao" = date('{}')
        ORDER BY "cnes_id" DESC
    """

extract_data_task = PythonOperator(
    task_id="extract_data_task",
    python_callable=extract_data,
    op_kwargs={"query": query},
    provide_context=True,
    dag=dag,
)

process_data_task = PythonOperator(
    task_id="process_data_task", python_callable=process_data, provide_context=True, dag=dag
)


sheet_id = "1g7PgVQqFSXcZhySLQahgA0Cz9AvMFVN71RF3F7z1SRk"
range_ = "covid19!A1:V"

upload_data_task = PythonOperator(
    task_id="upload_data_task",
    python_callable=upload_data,
    provide_context=True,
    op_kwargs={"sheet_id": sheet_id, "range": range_},
    dag=dag,
)

extract_data_task >> process_data_task >> upload_data_task


if __name__ == "__main__":
    update_healthcare_facilities([2065118, 2061252, 2087324, 6322646])
