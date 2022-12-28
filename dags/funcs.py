import pyathena
import pandas as pd

conn = pyathena.connect(s3_staging_dir="s3://guhls-lake/covid19-vac/", region_name="us-east-2")


def get_data(query):
    df = pd.read_sql_query(query, conn)
    return df


if __name__  == '__main__':
    get_data()