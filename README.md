# End-to-End Downstream Fuel Logistics & SCM Analytics Pipeline

Data Engineering pipeline designed to simulate, ingest, and transform downstream fuel distribution operations and tank storage telemetry (Pertalite, Biosolar, Pertamax) across Indonesian fuel terminals.

## Architecture Overview
- **Storage & Warehouse:** PostgreSQL 16 (Dockerized container)
- **Data Modeling & Transformation:** dbt-core (Medallion Architecture: Bronze -> Silver -> Gold)
- **Ingestion & Simulation:** Python (Synthetic generator modeling refinery origins, multi-modal transport, and daily storage telemetry)
- **Data Quality:** dbt Generic Tests (Uniqueness, Non-null, Accepted Values)
- **Orchestration:** Python Orchestrator (`run_pipeline.py`)

## Business Metrics Calculated
1. **Days of Inventory (Stock Coverage):** Evaluating terminal supply resilience against daily regional sales velocity.
2. **Stock Health Thresholds:** Classifying inventory into `CRITICAL_STOCK` (< 3 days), `SAFE_STOCK` (3–7 days), and `HIGH_STOCK` (> 7 days).
3. **Logistics SLA & OTIF:** Tracking transit variances, lead times, and delay patterns across transport modes (Tanker Vessel, Pipeline, Rail Wagon, Tanker Truck).

## Project Setup & Reproduction

### 1. Start Database Container
```bash
docker run -d \
  --name postgres-fuel-scm \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=fuel_scm_dw \
  -p 5433:5432 \
  -v fuel_scm_pgdata:/var/lib/postgresql/data \
  postgres:16-alpine