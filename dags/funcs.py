import pyathena
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

conn = pyathena.connect(
    s3_staging_dir=os.environ.get('S3_STAGING_DIR'), 
    region_name=os.environ.get('REGION_NAME')
    )


def get_data(query):
    df = pd.read_sql_query(query, conn)
    return df


if __name__  == '__main__':
    get_data()