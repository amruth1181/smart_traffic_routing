# ------------------------------------------------------------------
# Airflow DAG: orchestrates the daily batch ELT + analytics pipeline.
#
#   generate_data  ->  load_to_warehouse  ->  dbt_run  ->  dbt_test
#
# Any task failure triggers `task_failure_alert` (Slack webhook if
# SLACK_WEBHOOK_URL is set, otherwise it just logs).
#
# Deploy: copy this file into your Airflow `dags/` folder (or point
# AIRFLOW__CORE__DAGS_FOLDER at this directory) and set SMART_TRAFFIC_HOME.
# ------------------------------------------------------------------

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

# Absolute path to the project root on the machine running Airflow.
PROJECT_HOME = os.environ.get("SMART_TRAFFIC_HOME", "/opt/smart_traffic_routing")
DBT_DIR = os.path.join(PROJECT_HOME, "dbt")


def task_failure_alert(context):
    """Failure callback — posts to Slack if configured, else logs."""
    task = context.get("task_instance")
    msg = (
        f":red_circle: *Smart Traffic pipeline failed*\n"
        f"DAG: {task.dag_id}\nTask: {task.task_id}\n"
        f"Execution: {context.get('execution_date')}\n"
        f"Log: {task.log_url}"
    )
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook:
        try:
            import requests
            requests.post(webhook, json={"text": msg}, timeout=10)
        except Exception as e:  # never let the alert itself crash the run
            print(f"⚠️ Failed to send Slack alert: {e}")
    else:
        print(f"ALERT (no SLACK_WEBHOOK_URL set):\n{msg}")


default_args = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": task_failure_alert,
}

with DAG(
    dag_id="smart_traffic_pipeline",
    description="Daily ELT: generate -> load to warehouse -> dbt transform -> dbt test",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["data-engineering", "traffic", "elt", "dbt"],
) as dag:

    # 1) (Re)generate the synthetic source data. In a real pipeline this
    #    would be an extract from an API / source DB instead.
    generate_data = BashOperator(
        task_id="generate_data",
        bash_command=f"cd {PROJECT_HOME} && python generate_mock_traffic.py",
    )

    # 2) Load the enriched records into the warehouse `raw` schema.
    load_to_warehouse = BashOperator(
        task_id="load_to_warehouse",
        bash_command=f"cd {PROJECT_HOME} && python warehouse/load_to_postgres.py",
    )

    # 3) Transform raw -> staging -> marts with dbt.
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run --profiles-dir {DBT_DIR}",
    )

    # 4) Run data-quality tests. If any fail, the DAG fails and alerts.
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test --profiles-dir {DBT_DIR}",
    )

    generate_data >> load_to_warehouse >> dbt_run >> dbt_test
