import pandas as pd


def process_data(*args, **kwargs):
    data = kwargs['task_instance'].xcom_pull(task_ids='extract_data_task')
    df = pd.read_json(data)
    # Data Transform
    ...
    return df.to_json(orient='index', date_format='iso')
