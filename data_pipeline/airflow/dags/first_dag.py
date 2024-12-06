from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'lwjdonb',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}
with DAG(
    dag_id = 'first_dag',
    default_args = default_args,
    description = 'This is first dag that I write',
    start_date = datetime(2024, 11, 14, 7),
    schedule_interval=timedelta(minutes=1)
) as dag:
    task1 = BashOperator(
        task_id = 'first_task',
        bash_command='echo hello world, this is the fist task!'
    )
    
    task1