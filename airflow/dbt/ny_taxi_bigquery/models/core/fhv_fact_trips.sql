{{
    config(materialized='table')
}}

with fhv_tripdata as (
    select *, 
        'FHV' as service_type
    from {{ ref('stg_fhv_tripdata') }}
),
dim_zones as (
    select * from {{ ref('dim_zones') }}
    where borough != 'Unknown'
)
select 
    f.tripid,
    f.dispatching_base_num,
    f.pickup_locationid,
    pickup_zone.borough as pickup_borough, 
    pickup_zone.zone as pickup_zone, 
    f.dropoff_locationid,
    dropoff_zone.borough as dropoff_borough, 
    dropoff_zone.zone as dropoff_zone,
    f.sr_flag,
    f.affiliated_base_number,
    f.pickup_datetime,
    f.dropoff_datetime
from fhv_tripdata as f
inner join dim_zones as pickup_zone
on f.pickup_locationid = pickup_zone.locationid
inner join dim_zones as dropoff_zone
on f.dropoff_locationid = dropoff_zone.locationid