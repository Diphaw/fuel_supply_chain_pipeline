WITH shipments AS (
    SELECT * FROM {{ ref('stg_shipments') }}
),

terminals AS (
    SELECT * FROM {{ ref('stg_terminals') }}
)

SELECT
    s.shipment_id,
    s.origin_point,
    s.terminal_id,
    t.terminal_name AS destination_name,
    t.region AS destination_region,
    s.transport_mode,
    s.product_name,
    s.volume_kl,
    s.departure_time,
    s.estimated_arrival,
    s.actual_arrival,
    s.delivery_status,
    s.estimated_duration_hours,
    s.actual_duration_hours,
    s.delay_hours,
    -- Flag On-Time Delivery untuk perhitungan SLA
    CASE 
        WHEN s.delivery_status = 'ON_TIME' THEN 1 
        WHEN s.delivery_status = 'DELAYED' THEN 0 
        ELSE NULL 
    END AS is_on_time
FROM shipments s
LEFT JOIN terminals t ON s.terminal_id = t.terminal_id
