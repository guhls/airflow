![airflow_containers.png](https://docs.google.com/uc?id=1RM3_64kaIeTrxLBqHzIPVmHE2TnfLGVR)

- airflow-scheduler - The scheduler monitors all tasks and DAGs, then triggers the task instances once their dependencies are complete.
- airflow-webserver — The webserver is available at http://localhost:8080
- airflow-worker — The worker that executes the tasks given by the scheduler.
- airflow-init — The initialization service.
- flower — The flower app for monitoring the environment. It is available at http://localhost:5555.
postgres — The database.
- redis — The redis - broker that forwards messages from scheduler to worker.

# Running with Pypi

First all Check the airflow.cfg in ~/airflow/airflow.cfg and set up the dags_folder and load_examples vars

~~~shell
airflow db init
airflow webserver
airflow users create \
          --username admin \
          --firstname FIRST_NAME \
          --lastname LAST_NAME \
          --role Admin \
          --email admin@example.org
airflow scheduler
~~~