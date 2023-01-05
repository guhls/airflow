import pandas as pd
from googleapiclient.discovery import build

import auth
from tasks.athena.funcs import get_data


def extract_data(*args, **kwargs):
    date = str(kwargs["date"])

    query = f"""
        SELECT *
        FROM "final"."covid19_vac_sp_view"
        WHERE "vacina_dataaplicacao" = date('{date}')
        LIMIT 10
    """

    df = get_data(query)
    return df.to_json()


def upload_data(*args, **kwargs):
    data = kwargs["task_instance"].xcom_pull(task_ids="process_data_task")
    df = pd.read_json(data)

    service_sheets = build("sheets", "v4", credentials=auth.google.creds.get_creds()) # noqa

    sheet = service_sheets.spreadsheets()
    sheet_id = "1g7PgVQqFSXcZhySLQahgA0Cz9AvMFVN71RF3F7z1SRk"
    range_ = "covid19!A1"

    values = df.values.tolist()

    result = ( # noqa
        sheet.values()
        .update(
            spreadsheetId=sheet_id,
            range=range_,
            valueInputOption="RAW",
            body={"values": values},
        )
        .execute()
    )


if __name__ == "__main__":
    extract_data(date="2022-11-18")
