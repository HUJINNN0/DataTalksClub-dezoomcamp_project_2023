with finaldata as 
(
  select distinct*
  from {{ source('staging','chatgpt_before') }}
  where int64_field_0 is not null 
)