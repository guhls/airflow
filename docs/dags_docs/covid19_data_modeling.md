# Covid19 Data Modeling

> Objective: Populate some data of data.gov to a table in AWS Athena

## Requirements

### AWS Credentials

~~~shell
export AWS_ACCESS_KEY_ID=<aws_access_key_id>
export AWS_SECRET_ACCESS_KEY=<aws_secret_access_key>
export AWS_DEFAULT_REGION=<aws_default_region> 
~~~

### Google Cloud Credentials

- [Como criar uma conta/chave de serviço](https://developers.google.com/identity/protocols/oauth2/service-account#creatinganaccount)

- Save the key as credentials.json in the path /auth/ of this project

- In gsheets share with email created to service account

### Update .env

~~~env
 S3_STAGING_DIR=<s3_staging_dir>
 REGION_NAME=<region_name>
~~~

## Pipeline Flowchart

![flowchart_of_the_pipe](https://docs.google.com/uc?id=1PjAHf-yNlwsnR1Wqt4l7vj3MeVgZ-bCM)

## How the pipeline works

The pipeline follows an ETL flow with the following steps:

1. extract_data_task:
    - Extract data from the view covid19_vac_sp_view using the pandas library to create a dataframe and pyathena to create the connection
    - Converts and returns dataframe data in json

2. process_data_task:
    - working on it

3. upload_data_task:
    - Retrieve data from process_data_task  
    - Creates the connection to the "sheets" service using the googleapiclient lib
    - Load the data into the [Gsheet worksheet](https://docs.google.com/spreadsheets/d/1g7PgVQqFSXcZhySLQahgA0Cz9AvMFVN71RF3F7z1SRk/edit#gid=1762004493)

**Check the pipeline code here:** [covid19_data_modeling.py](https://github.com/guhls/airflow/blob/main/dags/covid19_data_modeling.py)

## Services Used

- Python Libs:
  - Pandas
  - Pyathena
  - Datetime
  - Google api client

- AWS services:
  - S3
  - Athena

- API:
  - Google sheets
