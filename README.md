[![wakatime](https://wakatime.com/badge/user/af93572d-f069-49a1-bc1e-6447fee29a9a/project/bf31cfea-d31f-4b6d-b315-830362fe8170.svg)](https://wakatime.com/badge/user/af93572d-f069-49a1-bc1e-6447fee29a9a/project/bf31cfea-d31f-4b6d-b315-830362fe8170)

# Final Goal
![flowchart_of_the_pipe](https://docs.google.com/uc?id=1PjAHf-yNlwsnR1Wqt4l7vj3MeVgZ-bCM)

# Steps to Install and Configure the enviroment

# Using Docker compose

Use the docker-compose.yaml in this repository, because alright set up with enviroments and additional requirements

Setting the right Airflow user
~~~shell
mkdir -p ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
~~~

Initialize the database
~~~shell
docker compose up airflow-init
~~~
# Running Airflow

## Credentials AWS
~~~shell
export AWS_ACCESS_KEY_ID=<aws_access_key_id>
export AWS_SECRET_ACCESS_KEY=<aws_secret_access_key>
export AWS_DEFAULT_REGION=<aws_default_region> 
~~~

Update .env, Add aws constraints
~~~
 S3_STAGING_DIR=<s3_staging_dir>
 REGION_NAME=<region_name>
~~~

~~~shell
docker-compose up
~~~

CLI commands
~~~shell
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.5.0/airflow.sh'
chmod +x airflow.sh
~~~

~~~shell
./airflow.sh info
./airflow.sh bash
./airflow.sh python
~~~

# Stopping containers

~~~shell
docker-compose down --volumes --remove-orphans
~~~

# Cleaning up

If want cleaning stop and delete conatiners 
~~~shell
docker-compose down --volumes --rmi all
~~~

---

# Added Credentials Google
[Credentials Google Console](https://console.cloud.google.com/apis/credentials?hl=pt-br&project=<PROJECT_NAME>)

Save the downloaded JSON file as credentials.json in dags/

---

# Process Final

![airflow_graph](https://docs.google.com/uc?id=1HqDIUJB2LvkB4ux6ViFxwrlbpoyvX13F)

[The DAG](https://github.com/guhls/airflow/blob/main/dags/covid19_data_modeling.py)

![data_in_google_sheets](https://docs.google.com/uc?id=1QoY_uKBcsEdXxsD9p4WEQ20BPCnIYweq)
Mantido um limit 10 na query na etapa extract_data_task

[The GSheet link](https://docs.google.com/spreadsheets/d/1g7PgVQqFSXcZhySLQahgA0Cz9AvMFVN71RF3F7z1SRk/edit#gid=1762004493)

