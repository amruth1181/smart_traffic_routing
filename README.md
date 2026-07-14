# 🚦 Smart Traffic Routing — Big Data, Machine Learning & Graph Algorithms

**Tagline:**  
**“Real-time congestion prediction with Kafka, Spark, XGBoost, and dynamic routing powered by graph algorithms.”**

---

![Big Data](https://img.shields.io/badge/BigData-Kafka%20%7C%20Spark-orange)  
![Streaming](https://img.shields.io/badge/Streaming-Structured%20Streaming-red)  
![ML](https://img.shields.io/badge/ML-XGBoost-blue)  
![Graph](https://img.shields.io/badge/Algorithms-A*-green)  
![Warehouse](https://img.shields.io/badge/Warehouse-Postgres-blue)  
![Transform](https://img.shields.io/badge/Transform-dbt-orange)  
![Orchestration](https://img.shields.io/badge/Orchestration-Airflow-teal)  
![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-yellow)  

📐 **See [ARCHITECTURE.md](ARCHITECTURE.md) for the full data-flow diagram and layer-by-layer breakdown.**

---

## ℹ️ About This Repository

This is a **personal reimplementation** built to demonstrate the architecture and
engineering patterns of a real-time data pipeline. It was inspired by professional
work I did on a company project — but **it shares no proprietary code, data, or
internal details from that project.**

- **All data here is synthetic** — generated locally by `generate_mock_traffic.py`.
  There is no real traffic, weather, or incident data from any company or third party.
- The code was rebuilt from scratch with generic component names and runs entirely
  on a local machine (local Kafka, local Spark, local MongoDB).
- The goal is to showcase the *skills and design* (streaming ingestion, stream
  processing, ML inference, graph routing) — not to reproduce any confidential system.

---

## 📘 Overview

Urban mobility faces major challenges: **congestion, delays, and inefficiency**. Reactive systems update only after congestion happens. Our solution is **proactive** — it **predicts congestion** based on traffic, weather, and incident data and dynamically adjusts routing.

This project is an **end-to-end data platform** combining:  
- **Data Engineering** (Kafka, Spark Structured Streaming, a Postgres **warehouse**, **dbt**, **Airflow**)  
- **Machine Learning** (XGBoost regression to predict traffic speed)  
- **Graph Algorithms** (A* Shortest Path with predicted edge constraints)  
- **Visualization** (Streamlit dashboard for real-time decision-making)  

### Core Highlights
- **Synthetic Data Generation:** Generates 15,000+ rows of realistic California highway traffic, weather, and incident data to simulate PeMS sensor metrics.
- **Kafka Streaming:** Simulates real-time IoT feeds via Kafka Producers for continuous data ingestion.
- **PySpark Processing:** Uses Spark Structured Streaming with watermarks and **stream-to-stream joins** to enrich incoming messages.
- **Warehouse + ELT:** Loads enriched records into a **Postgres** warehouse (`raw` schema), then transforms them with **dbt** into `staging` and `marts` layers using **SQL**.
- **Data Quality:** **dbt tests** (`not_null`, `accepted_values`) + **source freshness** checks guard the pipeline.
- **Orchestration:** An **Airflow** DAG schedules the daily ELT (generate → load → dbt run → dbt test) with retries and **failure alerting** (Slack).
- **Cloud-ready:** Every connection is **env-driven**, so local Postgres → Cloud SQL / BigQuery / Snowflake is a config change, not a code change.
- **XGBoost Inference:** Predicts freeway traversal speed based on current load, occupancy, and weather conditions.
- **A* Routing:** Dynamically adjusts pathfinding across the Bay Area road network based on the ML-predicted travel times.

---

## ⚙️ System Architecture

```
sources ─▶ Kafka ─▶ Spark (stream joins) ─▶ MongoDB
                                              │
                                   load_to_postgres.py
                                              ▼
                        Postgres warehouse: raw ─dbt▶ staging ─dbt▶ marts
                                              ▲            + dbt tests
                                       Airflow DAG (schedule + alerts)

        XGBoost speed model ─▶ A* routing ─▶ Streamlit dashboard
```

1. **Kafka Producers:** Stream synthetic traffic/incident data + real public weather as JSON to Kafka topics.
2. **Spark Streaming:** Consumes `traffic-data`, `weather-data`, `traffic-incidents`, applies watermarks, joins the three streams by location + time window, and writes enriched records to **MongoDB**.
3. **Warehouse Load (`warehouse/load_to_postgres.py`):** Extracts enriched records (Mongo, or CSV fallback) and loads them into the Postgres `raw` schema.
4. **dbt (`dbt/`):** Transforms `raw → staging → marts` with **SQL** and runs **data-quality tests** + source freshness.
5. **Airflow (`airflow/dags/`):** Orchestrates the daily ELT with retries and failure alerts.
6. **ML + Routing:** XGBoost predicts segment speed; A* over a NetworkX graph finds the fastest route; Streamlit visualizes it.

> Full details + diagram: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

---

## 🚀 How to Run Locally

### 1. Prerequisites
- Docker & Docker Compose (for Kafka + Postgres warehouse)
- Python 3.9+
- Apache Spark (PySpark)

Install the Python dependencies and set up your environment file:
```bash
pip install -r requirements.txt
cp .env.example .env      # then edit values if needed
```

### 2. Prepare the Data & Machine Learning Model
Generate the synthetic datasets and train the XGBoost model. This creates `traffic_weather_incidents.csv` and `pems_5min_cleaned_with_location.csv`, and outputs `traffic_speed_model.pkl` to the `models/` directory.
```bash
python3 generate_mock_traffic.py
python3 scripts/xgboost_model.py
```

### 3. Start Infrastructure (Kafka + Warehouse)
Spin up Kafka and the Postgres warehouse using Docker Compose:
```bash
docker-compose up -d
```
*Kafka runs on `localhost:9092`; Postgres warehouse on `localhost:5432`.*

### 4. Start the Streams
Open a new terminal to start sending simulated real-time telemetry to the local Kafka broker:
```bash
# Run these in separate terminals or in the background:
python3 streaming/kafka_traffic_producer.py &
python3 streaming/kafka_weather_producer.py &
python3 streaming/kafka_incident_producer.py &
```

*(Optional)* Run PySpark to observe the incoming multi-stream data:
```bash
python3 streaming/spark_traffic_stream.py
```

### 5. Run the Warehouse ELT (load → transform → test)
Land the enriched data in the warehouse and build the dbt models:
```bash
export $(grep -v '^#' .env | xargs)   # load env vars (or use direnv/python-dotenv)

python3 warehouse/load_to_postgres.py   # EL: enriched records -> Postgres raw.*
cd dbt
dbt run     --profiles-dir .            # Transform: raw -> staging -> marts
dbt test    --profiles-dir .            # Data-quality tests + freshness
dbt source freshness --profiles-dir .   # (optional) source freshness check
cd ..
```

### 6. (Optional) Orchestrate with Airflow
```bash
export SMART_TRAFFIC_HOME=$(pwd)
# point Airflow's dags_folder at ./airflow/dags, then trigger:
airflow dags trigger smart_traffic_pipeline
```
The DAG runs `generate_data ▶ load_to_warehouse ▶ dbt_run ▶ dbt_test` daily,
with retries and Slack failure alerts (set `SLACK_WEBHOOK_URL`).

### 7. Launch the Dashboard
Open the interactive mapping and routing UI:
```bash
streamlit run dashboard/dashboard.py
```
Access it at `http://localhost:8501`.

---

## ☁️ Cloud Deployment
Every connection is env-driven, so moving to the cloud is a config change:
Postgres → **Cloud SQL / BigQuery / Snowflake**, Kafka → **Confluent Cloud**,
Spark → **Dataproc**, Airflow → **Cloud Composer**. See
[ARCHITECTURE.md](ARCHITECTURE.md#3-cloud-path-free-tier).

---

## 📁 Repository Structure

- `generate_mock_traffic.py` — Synthetic PeMS traffic dataset generator.
- `docker-compose.yml` — Kafka + Postgres warehouse deployment.
- `streaming/` — Kafka producers and PySpark Structured Streaming jobs.
- `warehouse/load_to_postgres.py` — **EL step**: enriched records → Postgres `raw`.
- `dbt/` — **dbt project**: `raw → staging → marts` SQL models + data-quality tests.
- `airflow/dags/` — **Airflow DAG** orchestrating the daily ELT with alerting.
- `scripts/` — ML training pipeline (`xgboost_model.py`) + Mongo helpers.
- `A*/a_star_routing.py` — Routing logic using A* heuristics on the Bay Area graph.
- `dashboard/dashboard.py` — Interactive Streamlit application.
- `models/` — Exported ML models (`.pkl`, git-ignored; regenerate via training).
- `.env.example` — Environment variable template (copy to `.env`).
- `ARCHITECTURE.md` — Full architecture + data-flow documentation.
