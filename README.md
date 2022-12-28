# Steps to Install and Configure the enviroment

# Using Docker compose

Using the docker-compose.yaml in the repository

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

Save the downloaded JSON file as credentials.json