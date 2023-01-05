import os

import pandas as pd
import pyathena
from dotenv import load_dotenv

load_dotenv()

conn = pyathena.connect(
    s3_staging_dir=os.environ.get('S3_STAGING_DIR'),
    region_name=os.environ.get('REGION_NAME')
    )


def get_data(query):
    return pd.read_sql_query(query, conn)
