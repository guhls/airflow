import pandas as pd
from googleapiclient.discovery import build

from auth.google.creds import get_creds
from tasks.athena.funcs import get_data


def extract_data(*args, **kwargs):
    query = str(kwargs["query"])

    df = get_data(query)

    return df.to_json()


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


if __name__ == "__main__":
    extract_data(date="2022-11-18")
