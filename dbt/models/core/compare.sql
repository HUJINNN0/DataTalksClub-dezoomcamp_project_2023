{{ config(materialized='table') }}

with final_data as (
    select *
    from {{ ref('stg_chat_before') }}
), 

finaldata as (
    select * from {{ ref('pickle_file') }}
)
select 
    final_data.videoId, 
    final_data.publishedAt, 
    final_data.channelType,
    final_data.channelID, 
    final_data.channelTitle, 
    final_data.viewCount

from final_data
inner join pickle_file as chatgpt_after
on final_data.chatgpt_after = rev_zone.chatgpt_after
inner join pickle_file as chatgpt_before
on final_data.chatgpt_before = rev_zone.chatgpt_before