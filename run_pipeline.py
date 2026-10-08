import subprocess
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def run_command(cmd, cwd=None):
    logging.info(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        logging.error(f"Command failed with error:\n{result.stderr}")
        sys.exit(1)
    logging.info(f"Success:\n{result.stdout.strip()[-300:]}\n")

def main():
    start_time = datetime.now()
    logging.info("=== STARTING FUEL SCM PIPELINE ===")

    # 1. Ingestion / Data Generation
    logging.info("Step 1: Ingesting Simulated Fuel Logistics Data...")
    run_command(["python", "data_generator/generate_fuel_data.py"])

    # 2. dbt Transform (Silver & Gold)
    logging.info("Step 2: Executing dbt Transformation Models...")
    run_command(["dbt", "run"], cwd="transform")

    # 3. dbt Testing (Data Quality)
    logging.info("Step 3: Executing dbt Quality Tests...")
    run_command(["dbt", "test"], cwd="transform")

    elapsed = datetime.now() - start_time
    logging.info(f"=== PIPELINE FINISHED SUCCESSFULLY IN {elapsed.total_seconds():.2f}s ===")

if __name__ == "__main__":
    main()
