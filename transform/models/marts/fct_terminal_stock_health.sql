WITH storage AS (
    SELECT * FROM {{ ref('stg_daily_storage') }}
),

terminals AS (
    SELECT * FROM {{ ref('stg_terminals') }}
)

SELECT
    s.record_date,
    s.terminal_id,
    t.terminal_name,
    t.region,
    s.product_name,
    s.current_stock_kl,
    s.daily_consumption_kl,
    -- Formula Days of Inventory (Stock Days Coverage)
    ROUND(s.current_stock_kl / NULLIF(s.daily_consumption_kl, 0), 2) AS days_of_inventory,
    -- Rasio Utilisasi Kapasitas Tangki Terminal
    ROUND((s.current_stock_kl / NULLIF(t.total_capacity_kl, 0)) * 100, 2) AS tank_utilization_pct,
    -- Klasifikasi Ambang Batas Ketahanan Pasokan SCM
    CASE
        WHEN (s.current_stock_kl / NULLIF(s.daily_consumption_kl, 0)) < 3.0 THEN 'CRITICAL_STOCK'
        WHEN (s.current_stock_kl / NULLIF(s.daily_consumption_kl, 0)) BETWEEN 3.0 AND 7.0 THEN 'SAFE_STOCK'
        ELSE 'HIGH_STOCK'
    END AS stock_health_status
FROM storage s
LEFT JOIN terminals t ON s.terminal_id = t.terminal_id
