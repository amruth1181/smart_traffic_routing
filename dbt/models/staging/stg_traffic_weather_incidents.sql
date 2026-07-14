-- Staging model: clean + cast the raw records into a tidy, typed table.
-- One row per observation. Downstream marts build on this.

with source as (

    select * from {{ source('raw', 'traffic_weather_incidents') }}

),

cleaned as (

    select
        -- event time: prefer the record's own timestamp, else the load time
        coalesce(
            nullif(cast("time" as varchar), '')::timestamp,
            _loaded_at
        )                                             as event_time,

        cast(station_id as integer)                   as station_id,
        cast(freeway as varchar)                      as freeway,
        upper(coalesce(cast(direction as varchar), 'UNKNOWN')) as direction,
        coalesce(cast(lane_type as varchar), 'UNKNOWN')        as lane_type,

        cast(flow as double precision)                as flow,
        cast(occupancy as double precision)           as occupancy,
        cast(speed as double precision)               as speed,

        coalesce(cast(region as varchar), 'UNKNOWN')  as region,
        cast(temperature as double precision)         as temperature,
        cast(windspeed as double precision)           as windspeed,
        cast(weathercode as integer)                  as weathercode,

        lower(coalesce(cast(incident_type as varchar), 'none')) as incident_type,
        lower(coalesce(cast(severity as varchar), 'none'))      as severity,

        _loaded_at
    from source

)

select *
from cleaned
-- drop rows with no measured speed (nothing to analyze/predict from)
where speed is not null
