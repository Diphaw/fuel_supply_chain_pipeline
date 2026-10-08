import os
import random
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

load_dotenv()

# Koneksi ke PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT")
)
cur = conn.cursor()

# 1. Pastikan Skema dan Tabel Raw Terbentuk
cur.execute("CREATE SCHEMA IF NOT EXISTS fuel_raw;")

cur.execute("""
CREATE TABLE IF NOT EXISTS fuel_raw.master_terminals (
    terminal_id VARCHAR(10) PRIMARY KEY,
    terminal_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    total_capacity_kl INT NOT NULL,
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6)
);

CREATE TABLE IF NOT EXISTS fuel_raw.fuel_shipments (
    shipment_id VARCHAR(20) PRIMARY KEY,
    origin_point VARCHAR(100) NOT NULL,
    destination_terminal_id VARCHAR(10) REFERENCES fuel_raw.master_terminals(terminal_id),
    transport_mode VARCHAR(20) NOT NULL,
    product_name VARCHAR(50) NOT NULL,
    volume_kl INT NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    estimated_arrival TIMESTAMP NOT NULL,
    actual_arrival TIMESTAMP,
    delivery_status VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS fuel_raw.daily_tank_storage (
    storage_id SERIAL PRIMARY KEY,
    record_date DATE NOT NULL,
    terminal_id VARCHAR(10) REFERENCES fuel_raw.master_terminals(terminal_id),
    product_name VARCHAR(50) NOT NULL,
    current_stock_kl NUMERIC(10, 2) NOT NULL,
    daily_consumption_kl NUMERIC(10, 2) NOT NULL
);
""")

# Kosongkan data lama tanpa menghapus struktur tabel dan view yang bergantung padanya
cur.execute("""
TRUNCATE TABLE fuel_raw.daily_tank_storage, fuel_raw.fuel_shipments, fuel_raw.master_terminals CASCADE;
""")
conn.commit()

# 2. Master Data Terminal BBM
terminals_data = [
    ("IT-PLJ", "Integrated Terminal Plaju", "Sumbagsel", 85000, -2.9904, 104.8340),
    ("IT-JKT", "Integrated Terminal Jakarta (Plumpang)", "JBB", 120000, -6.1365, 106.8996),
    ("IT-BAL", "Integrated Terminal Balongan", "JBB", 75000, -6.3688, 108.3892),
    ("FT-RWL", "Fuel Terminal Rewulu", "JBT", 45000, -7.8016, 110.2831),
    ("FT-BYL", "Fuel Terminal Boyolali", "JBT", 38000, -7.5358, 110.5960),
    ("IT-SBY", "Integrated Terminal Surabaya (Tanjung Perak)", "Jatimbalinus", 110000, -7.2025, 112.7278),
    ("FT-TBN", "Fuel Terminal Tuban", "Jatimbalinus", 60000, -6.8997, 112.0461),
    ("IT-MKS", "Integrated Terminal Makassar", "Sulawesi", 65000, -5.1189, 119.4144)
]

cur.executemany("""
    INSERT INTO fuel_raw.master_terminals VALUES (%s, %s, %s, %s, %s, %s);
""", terminals_data)

# 3. Generate Transaksi Logistik (Shipments)
supply_origins = ["Refinery Unit III Plaju", "Refinery Unit VI Balongan", "Refinery Unit IV Cilacap", "Refinery Unit V Balikpapan"]
products = ["Pertalite", "Biosolar", "Pertamax"]
transport_modes = ["Tanker Vessel", "Pipeline", "Rail Wagon", "Tanker Truck"]

shipments = []
base_time = datetime.now() - timedelta(days=14)

for i in range(1, 301):
    shp_id = f"SHP-{i:05d}"
    origin = random.choice(supply_origins)
    dest = random.choice(terminals_data)[0]
    mode = random.choice(transport_modes)
    prod = random.choice(products)
    
    if mode == "Tanker Vessel":
        vol = random.randint(2000, 8000)
        travel_hours = random.randint(24, 72)
    elif mode == "Pipeline":
        vol = random.randint(1500, 4000)
        travel_hours = random.randint(6, 18)
    elif mode == "Rail Wagon":
        vol = random.randint(300, 900)
        travel_hours = random.randint(8, 20)
    else:
        vol = random.choice([16, 24, 32])
        travel_hours = random.randint(3, 10)

    dept_time = base_time + timedelta(hours=random.randint(1, 300))
    eta = dept_time + timedelta(hours=travel_hours)
    
    rand_status = random.random()
    if rand_status < 0.15:
        act_arrival = None
        status = "IN_TRANSIT"
    elif rand_status < 0.35:
        delay_hrs = random.randint(2, 12)
        act_arrival = eta + timedelta(hours=delay_hrs)
        status = "DELAYED"
    else:
        early_or_exact = random.choice([0, 0, -1, -2])
        act_arrival = eta + timedelta(hours=early_or_exact)
        status = "ON_TIME"

    shipments.append((shp_id, origin, dest, mode, prod, vol, dept_time, eta, act_arrival, status))

execute_batch(cur, """
    INSERT INTO fuel_raw.fuel_shipments VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
""", shipments)

# 4. Generate Telemetri Stok Tangki Harian (Daily Storage)
daily_records = []
for day_offset in range(14):
    curr_date = (base_time + timedelta(days=day_offset)).date()
    for term in terminals_data:
        t_id = term[0]
        for prod in products:
            avg_daily_sales = random.uniform(300, 1800)
            days_cover = random.choice([1.8, 2.5, 4.0, 5.5, 7.0, 11.5])
            stock_kl = round(avg_daily_sales * days_cover, 2)
            
            daily_records.append((curr_date, t_id, prod, stock_kl, round(avg_daily_sales, 2)))

execute_batch(cur, """
    INSERT INTO fuel_raw.daily_tank_storage (record_date, terminal_id, product_name, current_stock_kl, daily_consumption_kl)
    VALUES (%s, %s, %s, %s, %s);
""", daily_records)

conn.commit()
cur.close()
conn.close()

print("Data simulasi downstream SCM berhasil dimuat ulang:")
print(f"- {len(terminals_data)} Master Terminal")
print(f"- {len(shipments)} Log Shipments")
print(f"- {len(daily_records)} Catatan Telemetri Tangki Harian")
