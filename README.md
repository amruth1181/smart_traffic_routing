# 🚦 Smart Traffic Routing — Big Data, Machine Learning & Graph Algorithms

**Tagline:**  
**“Real-time congestion prediction with Kafka, Spark, XGBoost, and dynamic routing powered by graph algorithms.”**

---

![Big Data](https://img.shields.io/badge/BigData-Kafka%20%7C%20Spark-orange)  
![Streaming](https://img.shields.io/badge/Streaming-Structured%20Streaming-red)  
![ML](https://img.shields.io/badge/ML-XGBoost-blue)  
![Graph](https://img.shields.io/badge/Algorithms-A*-green)  
![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-yellow)  

---

## 📘 Overview

Urban mobility faces major challenges: **congestion, delays, and inefficiency**. Reactive systems update only after congestion happens. Our solution is **proactive** — it **predicts congestion** based on traffic, weather, and incident data and dynamically adjusts routing.

This project is an **end-to-end Big Data system** combining:  
- **Data Engineering** (Kafka, Spark Structured Streaming)  
- **Machine Learning** (XGBoost regression to predict traffic speed)  
- **Graph Algorithms** (A* Shortest Path with predicted edge constraints)  
- **Visualization** (Streamlit dashboard for real-time decision-making)  

### Core Highlights
- **Synthetic Data Generation:** Generates 15,000+ rows of realistic California highway traffic, weather, and incident data to simulate PeMS sensor metrics.
- **Kafka Streaming:** Simulates real-time IoT feeds via Kafka Producers for continuous data ingestion.
- **PySpark Processing:** Uses Spark Structured Streaming to aggregate and process incoming messages.
- **XGBoost Inference:** Predicts freeway traversal speed based on current load, occupancy, and weather conditions.
- **A* Routing:** Dynamically adjusts pathfinding across the Bay Area road network based on the ML-predicted travel times.

---

## ⚙️ System Architecture

1. **Kafka Producers:** Fetch synthetic data (`pems_5min_cleaned_with_location.csv`) and continuously stream JSON messages to Kafka.
2. **Spark Streaming:** Consumes Kafka topics (`traffic-data`, `weather-data`, `traffic-incidents`), sanitizes payloads, and prints aggregations to console / checkpoints.
3. **ML Layer:** An XGBoost model trained on historical data predicts vehicle speed (`km/h`) on specific road segments considering weather and traffic flows.
4. **Routing Engine:** The Streamlit dashboard builds a NetworkX graph of Bay Area intersection nodes. The A* algorithm utilizes predicted edge speeds to find the optimal path between stations.

---

## 🚀 How to Run Locally

### 1. Prerequisites
- Docker & Docker Compose (for Kafka/Zookeeper)
- Python 3.9+
- Apache Spark (PySpark)

Install the Python dependencies:
```bash
pip install pandas numpy xgboost scikit-learn networkx streamlit kafka-python-ng geopy pyspark
```

### 2. Prepare the Data & Machine Learning Model
Generate the synthetic datasets and train the XGBoost model. This creates `traffic_weather_incidents.csv` and `pems_5min_cleaned_with_location.csv`, and outputs `traffic_speed_model.pkl` to the `models/` directory.
```bash
python3 generate_mock_traffic.py
python3 scripts/xgboost_model.py
```

### 3. Start Apache Kafka
Spin up a local Kafka cluster using Docker Compose:
```bash
docker-compose up -d
```
*Note: Kafka runs on `localhost:9092`.*

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

### 5. Launch the Dashboard
Open the interactive mapping and routing UI:
```bash
streamlit run dashboard/dashboard.py
```
Access it at `http://localhost:8501`.

---

## 📁 Repository Structure

- `A*/a_star_routing.py` — Standalone routing logic using A* heuristics on the Bay Area graph.
- `dashboard/dashboard.py` — Interactive Streamlit application.
- `models/` — Contains exported ML models (`.pkl`).
- `scripts/` — ML training pipelines (`xgboost_model.py` and `data_preprocessing.py`).
- `streaming/` — Kafka Producers and PySpark Streams.
- `generate_mock_traffic.py` — Synthetic PeMS traffic dataset generator.
- `docker-compose.yml` — Kafka/Zookeeper deployment.
