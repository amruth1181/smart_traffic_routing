-- Mart: hourly time-series rollup of traffic conditions per region.
-- Demonstrates a time-bucketed aggregation (date_trunc) — a DE staple.

with stg as (

    select * from {{ ref('stg_traffic_weather_incidents') }}

)

select
    date_trunc('hour', event_time)          as traffic_hour,
    region,
    count(*)                                as observations,
    round(avg(speed)::numeric, 2)           as avg_speed_kmh,
    round(min(speed)::numeric, 2)           as min_speed_kmh,
    round(max(speed)::numeric, 2)           as max_speed_kmh,
    round(avg(flow)::numeric, 2)            as avg_flow,
    sum(case when incident_type <> 'none' then 1 else 0 end) as incident_count
from stg
group by date_trunc('hour', event_time), region
order by traffic_hour desc, region
