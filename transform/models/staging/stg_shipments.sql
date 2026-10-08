WITH source AS (
    SELECT * FROM {{ source('fuel_raw', 'fuel_shipments') }}
)

SELECT
    shipment_id,
    origin_point,
    destination_terminal_id AS terminal_id,
    transport_mode,
    product_name,
    volume_kl,
    departure_time,
    estimated_arrival,
    actual_arrival,
    delivery_status,
    -- Hitung estimasi jam perjalanan
    ROUND(EXTRACT(EPOCH FROM (estimated_arrival - departure_time)) / 3600, 2) AS estimated_duration_hours,
    -- Hitung realisasi jam perjalanan jika sudah tiba
    CASE 
        WHEN actual_arrival IS NOT NULL 
        THEN ROUND(EXTRACT(EPOCH FROM (actual_arrival - departure_time)) / 3600, 2)
        ELSE NULL 
    END AS actual_duration_hours,
    -- Hitung selisih keterlambatan (jam)
    CASE 
        WHEN actual_arrival IS NOT NULL 
        THEN ROUND(EXTRACT(EPOCH FROM (actual_arrival - estimated_arrival)) / 3600, 2)
        ELSE NULL 
    END AS delay_hours
FROM source
