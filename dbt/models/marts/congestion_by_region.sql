-- Mart: congestion profile per region + freeway.
-- This is the kind of SQL aggregation a DE ships for analysts/dashboards.

with stg as (

    select * from {{ ref('stg_traffic_weather_incidents') }}

),

aggregated as (

    select
        region,
        freeway,
        count(*)                                        as observations,
        round(avg(speed)::numeric, 2)                   as avg_speed_kmh,
        round(avg(flow)::numeric, 2)                    as avg_flow,
        round(avg(occupancy)::numeric, 4)               as avg_occupancy,
        round(avg(temperature)::numeric, 1)             as avg_temperature,
        sum(case when incident_type <> 'none' then 1 else 0 end) as incident_count
    from stg
    group by region, freeway

)

select
    *,
    -- simple business rule: average speed under 40 km/h = congested corridor
    (avg_speed_kmh < 40) as is_congested
from aggregated
order by avg_speed_kmh asc
