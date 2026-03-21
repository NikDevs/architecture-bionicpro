from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
from clickhouse_driver import Client

default_args = {
    'owner': 'bionicpro',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'etl_user_reports',
    default_args=default_args,
    schedule_interval='0 * * * *',  # каждый час
    start_date=datetime(2024, 1, 1),
    catchup=False
)

def extract_crm():
    conn = psycopg2.connect(
        dbname="crm_db",
        user="user",
        password="password",
        host="crm"
    )
    cur = conn.cursor()
    cur.execute("SELECT user_id, prosthesis_id FROM users")
    return cur.fetchall()

def extract_telemetry():
    conn = psycopg2.connect(
        dbname="telemetry_db",
        user="user",
        password="password",
        host="telemetry"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT prosthesis_id, COUNT(*) as total_movements,
               AVG(signal) as avg_signal,
               MAX(timestamp) as last_activity
        FROM telemetry
        GROUP BY prosthesis_id
    """)
    return cur.fetchall()

def load_to_clickhouse(**context):
    crm_data = context['ti'].xcom_pull(task_ids='extract_crm')
    telemetry_data = context['ti'].xcom_pull(task_ids='extract_telemetry')

    client = Client(host='clickhouse')

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

    client.execute(
        'INSERT INTO user_reports VALUES',
        result
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
    task_id='load_to_clickhouse',
    python_callable=load_to_clickhouse,
    provide_context=True,
    dag=dag
)

extract_crm_task >> extract_telemetry_task >> load_task