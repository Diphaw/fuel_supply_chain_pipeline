WITH source AS (
    SELECT * FROM {{ source('fuel_raw', 'master_terminals') }}
)

SELECT
    terminal_id,
    terminal_name,
    region,
    total_capacity_kl,
    latitude,
    longitude
FROM source
