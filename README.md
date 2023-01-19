[![wakatime](https://wakatime.com/badge/user/af93572d-f069-49a1-bc1e-6447fee29a9a/project/bf31cfea-d31f-4b6d-b315-830362fe8170.svg)](https://wakatime.com/badge/user/af93572d-f069-49a1-bc1e-6447fee29a9a/project/bf31cfea-d31f-4b6d-b315-830362fe8170)

# Steps to Install and Configure the enviroment

## Using Docker compose

- Use the docker-compose.yaml of this repository, because alright set up for this project

Setting the right Airflow user
~~~shell
mkdir -p ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
~~~

Initialize the database
~~~shell
docker compose up airflow-init
~~~

## Running Airflow

### Credentials AWS
~~~shell
export AWS_ACCESS_KEY_ID=<aws_access_key_id>
export AWS_SECRET_ACCESS_KEY=<aws_secret_access_key>
export AWS_DEFAULT_REGION=<aws_default_region> 
~~~

### Credentials Google Cloud
- [Como criar uma conta/chave de serviço](https://developers.google.com/identity/protocols/oauth2/service-account#creatinganaccount)

- Save the key as credentials.json in the path /auth/ of this project

- In gsheets share with email created to service account

### Update .env
~~~
 S3_STAGING_DIR=<s3_staging_dir>
 REGION_NAME=<region_name>
~~~

### CLI commands(Optional)
~~~shell
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.5.0/airflow.sh'
chmod +x airflow.sh

./airflow.sh info
./airflow.sh bash
./airflow.sh python
~~~

### Build airflow_custom image
~~~shell
docker build -t airflow_custom .
~~~

### Run container
~~~shell
docker-compose up
~~~

## Stopping containers

~~~shell
docker-compose down --volumes --remove-orphans
~~~

## Cleaning up (if necessary)

If want cleaning stop and delete conatiners 
~~~shell
docker-compose down --volumes --rmi all
~~~

# DAGs docs
