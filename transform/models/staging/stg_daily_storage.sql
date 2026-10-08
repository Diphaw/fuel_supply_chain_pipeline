WITH source AS (
    SELECT * FROM {{ source('fuel_raw', 'daily_tank_storage') }}
)

SELECT
    storage_id,
    record_date,
    terminal_id,
    product_name,
    current_stock_kl,
    daily_consumption_kl
FROM source
