# Airflow Repository

[![wakatime](https://wakatime.com/badge/user/af93572d-f069-49a1-bc1e-6447fee29a9a/project/bf31cfea-d31f-4b6d-b315-830362fe8170.svg)](https://wakatime.com/badge/user/af93572d-f069-49a1-bc1e-6447fee29a9a/project/bf31cfea-d31f-4b6d-b315-830362fe8170)

## Steps to Install and Configure the environment using Docker compose

### 1. Clone this repository

> The `docker-compose.yaml` of this repository alright set up for this project

### 2. Setting the right Airflow user

~~~shell
mkdir -p ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
~~~

### 3. Initialize the database

~~~shell
docker compose up airflow-init
~~~

### 4. Check the environments requirements for the DAGs in this repository

List of the DAGs docs:

- [covid19_data_modeling](https://github.com/guhls/airflow/blob/main/docs/dags_docs/covid19_data_modeling.md#Requirements)

### 5. CLI commands(Optional)

~~~shell
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.5.0/airflow.sh'
chmod +x airflow.sh

./airflow.sh info
./airflow.sh bash
./airflow.sh python
~~~

### 6. Build airflow_custom image

~~~shell
docker build -t airflow_custom .
~~~

### 7. Run and stopping containers

Running containers

~~~shell
docker-compose up
~~~

Stopping containers

~~~shell
docker-compose down --volumes --remove-orphans
~~~

Cleaning up (if necessary)

~~~shell
docker-compose down --volumes --rmi all
~~~
