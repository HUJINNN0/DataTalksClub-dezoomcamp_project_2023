with finaldata as 
(
  select distinct*
  from {{ source('staging','chatgpt_after') }}
  where int64_field_0 is not null 
)