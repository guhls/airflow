from airflow.operators.bash import BashOperator

from airflow import DAG

default_args = {
    "owner": 'guhls',
    "schedule_interval": '@daily'
}

dag = DAG(dag_id='load_flat_file_in_s3', default_args=default_args)

command = "wget -i {{ params.filename }}"

get_file_from_url = BashOperator(
    task_id='get_file_from_url',
    bash_command=command,
    params={'filename': 'urls.txt'},
    dag=dag
)

