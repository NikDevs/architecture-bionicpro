from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from clickhouse_driver import Client

default_args = {
    'owner': 'bionicpro',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'etl_user_reports',
    default_args=default_args,
    description='ETL pipeline for user reports',
    schedule_interval='*/5 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False
)

def create_table():
    client = Client(
        host="clickhouse",
        port=9000,
        user="default",
        password="password"
    )

    client.execute("""
       CREATE TABLE IF NOT EXISTS user_reports (
           user_id String,
           prosthesis_id String,
           total_movements UInt32,
           avg_signal Float32,
           last_activity DateTime,
           report_date Date
       )
       ENGINE = MergeTree()
       ORDER BY (user_id, report_date)
       """)

def extract_crm():
    return [
        ("prothetic1", "prosthesis1"),
        ("prothetic2", "prosthesis2"),
        ("prothetic3", "prosthesis3"),
    ]

def extract_telemetry():
    now = datetime.now()

    return [
        ("prosthesis1", 120, 0.85, now),
        ("prosthesis2", 80, 0.65, now),
        ("prosthesis3", 200, 0.90, now),
    ]

def transform_and_load(**context):
    crm_data = context['ti'].xcom_pull(task_ids='extract_crm')
    telemetry_data = context['ti'].xcom_pull(task_ids='extract_telemetry')

    client = Client(
        host="clickhouse",
        port=9000,
        user="default",
        password="password"
    )

    result = []

    for user_id, prosthesis_id in crm_data:
        for t in telemetry_data:
            if t[0] == prosthesis_id:
                result.append((
                    user_id,
                    prosthesis_id,
                    t[1],
                    t[2],
                    t[3],
                    datetime.now().date()
                ))

    if result:
        client.execute(
            "INSERT INTO user_reports VALUES",
            result
        )

create_table_task = PythonOperator(
    task_id='create_table',
    python_callable=create_table,
    dag=dag
)

extract_crm_task = PythonOperator(
    task_id='extract_crm',
    python_callable=extract_crm,
    dag=dag
)

extract_telemetry_task = PythonOperator(
    task_id='extract_telemetry',
    python_callable=extract_telemetry,
    dag=dag
)

load_task = PythonOperator(
    task_id='transform_and_load',
    python_callable=transform_and_load,
    provide_context=True,
    dag=dag
)

create_table_task >> extract_crm_task >> extract_telemetry_task >> load_task