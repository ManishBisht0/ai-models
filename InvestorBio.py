#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import random
import re
import datetime
from azure.cosmos import CosmosClient
import os

client = CosmosClient(endpoint, key)
database_name = 'heimdall-db'

def fetch_data_from_cosmos(container_name, query):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    items = container.query_items(query, enable_cross_partition_query=True)
    return list(items)

stage_mapping = {
    'Seed Stage': {'SEED PLUS', 'SEED 2', 'SEED 3', 'LATE-SEED', 'PRE SEED', 'SEED', 'SEED EXTENSION', 'POST-SEED', 'PRE-SEED', 'ANGEL', 'CROWDFUNDING', 'PRE-SEED-A'}, 
    'Early Stage': {'PRE-SERIES-A', 'PRE-SERIES-A1', 'A', 'A EXTENSION', 'A1', 'A2', 'A3', 'A+', 'PRE-SERIES-B'},
    'Later Stage': {'B2', 'C1', 'C2', 'D EXTENSION', 'C', 'C EXTENSION', 'G', 'C3', 'B', 'D', 'D2', 'PRE-SERIES-C', 'E', 'B3', 'B EXTENSION', 'D1', 'G EXTENSION', 'PRE-SERIES-D', 'B1', 'B+', 'G2', 'F', 'B3 EXTENSION', 'G1', 'J', 'I', 'H'}
}
series_to_stage = {series: stage for stage, series_set in stage_mapping.items() for series in series_set}

def map_series_to_stage(series):
    if series in series_to_stage:
        return series_to_stage[series]
    if re.match(r'^[B-Z][0-9]*[\+\-]?$', series, re.IGNORECASE):
        return 'Later Stage'
    return "Null"

def generate_description(row, df_deal):
    investor_name = row['Investor']
    
    if not isinstance(row.get('Investor_Deal_Ids'), list) or not row.get('Investor_Deal_Ids'):
        return f"{investor_name} has no confirmed or updated deals available."
    
    inv_deal = df_deal[df_deal['id'].isin(row['Investor_Deal_Ids'])]
    
    if inv_deal.empty:
        return f"{investor_name} has no confirmed or updated deals available."
    
    inv_deal = inv_deal.sort_values(by='published_date', ascending=False)
    
    stage = inv_deal['Series_Stage'].max()
    sectors = ', '.join(inv_deal['Main_Sector'].value_counts().head(3).index.tolist())
    
    top_10_investee_list = inv_deal['Corrected_Investee'].dropna().unique()[:10]
    top_10_investee = ', '.join(top_10_investee_list)

    
    no_stage_formats = [
        f"{investor_name} has recently invested in various notable companies such as {top_10_investee}. The majority of sectors {investor_name} has invested in include {sectors}.",
        f"In recent investments, {investor_name} has funded companies like {top_10_investee}, primarily focusing on sectors such as {sectors}.",
        f"The sectors {investor_name} has invested in most frequently include {sectors}, with notable investments in {top_10_investee}.",
        f"Among the top companies {investor_name} has invested in are {top_10_investee}, with major sectors being {sectors}.",
        f"Companies like {top_10_investee} have recently received investments from {investor_name}, who mainly focuses on sectors like {sectors}.",
        f"Prominent investments by {investor_name} include {top_10_investee}, particularly in sectors such as {sectors}.",
        f"Sectors like {sectors} have been the main focus of {investor_name}, with significant investments in companies like {top_10_investee}.",
        f"Recently, {investor_name} has invested in top companies such as {top_10_investee}, with a focus on sectors including {sectors}.",
        f"The recent investments by {investor_name} in companies like {top_10_investee} reflect a focus on sectors like {sectors}.",
        f"Top companies such as {top_10_investee} have seen investments from {investor_name}, who primarily targets sectors like {sectors}.",
        f"With a focus on sectors like {sectors}, {investor_name} has invested in notable companies such as {top_10_investee}.",
        f"Investments by {investor_name} have included notable companies like {top_10_investee}, mainly in sectors such as {sectors}.",
        f"Notable investments by {investor_name} include {top_10_investee}, with a primary focus on sectors like {sectors}.",
        f"Focusing on sectors like {sectors}, {investor_name} has recently invested in top companies such as {top_10_investee}.",
        f"Companies such as {top_10_investee} have seen investments from {investor_name}, who targets sectors like {sectors}.",
        f"The major sectors {investor_name} invests in include {sectors}, with notable companies like {top_10_investee} being recent recipients.",
        f"Among the sectors {investor_name} invests in are {sectors}, with significant investments in companies like {top_10_investee}.",
        f"Recent investments by {investor_name} include top companies like {top_10_investee}, primarily in sectors such as {sectors}.",
        f"In sectors like {sectors}, {investor_name} has made notable investments in companies such as {top_10_investee}.",
        f"Top investees of {investor_name} include {top_10_investee}, with a major focus on sectors like {sectors}.",
        f"Focusing on sectors such as {sectors}, {investor_name} has invested in notable companies like {top_10_investee}."
    ]
    
    with_stage_format = [
        f"{investor_name} primarily focuses on {stage} investments. Recently, it has invested in notable companies such as {top_10_investee}. The majority of sectors {investor_name} has invested in include {sectors}."
        f"Focusing primarily on {stage} investments, {investor_name} has recently invested in notable companies such as {top_10_investee}, with major sectors including {sectors}.",
        f"Recently, {investor_name} has invested in companies like {top_10_investee}, primarily focusing on {stage} investments in sectors such as {sectors}.",
        f"The sectors {investor_name} has invested in most frequently include {sectors}, with notable investments in {top_10_investee} at the {stage} stage.",
        f"{investor_name} has made {stage} investments in notable companies such as {top_10_investee}, mainly in sectors like {sectors}.",
        f"With a focus on {stage} investments, {investor_name} has recently invested in companies like {top_10_investee} in sectors such as {sectors}.",
        f"The primary focus of {investor_name} is on {stage} investments, with recent investments in companies like {top_10_investee} across sectors like {sectors}.",
        f"Notable companies such as {top_10_investee} have seen investments from {investor_name}, who primarily focuses on {stage} investments in sectors like {sectors}.",
        f"Focusing on {stage} investments, {investor_name} has recently invested in top companies such as {top_10_investee}, particularly in sectors like {sectors}.",
        f"Top companies like {top_10_investee} have received investments from {investor_name}, which focuses mainly on {stage} investments in sectors like {sectors}.",
        f"The major sectors {investor_name} invests in include {sectors}, with notable {stage} investments in companies like {top_10_investee}.",
        f"Investments by {investor_name} primarily focus on {stage} investments, with significant recent investments in companies like {top_10_investee} across sectors like {sectors}.",
        f"Notable {stage} investments by {investor_name} include companies such as {top_10_investee}, with a primary focus on sectors like {sectors}.",
        f"Among the sectors {investor_name} invests in are {sectors}, with recent notable {stage} investments in companies like {top_10_investee}.",
        f"Focusing on {stage} investments, {investor_name} has invested in top companies such as {top_10_investee} across sectors like {sectors}.",
        f"Companies like {top_10_investee} have recently received investments from {investor_name}, who focuses on {stage} investments in sectors such as {sectors}.",
        f"The sectors {investor_name} primarily invests in include {sectors}, with notable {stage} investments in companies like {top_10_investee}.",
        f"Recent investments by {investor_name} include top companies like {top_10_investee}, primarily at the {stage} stage and in sectors such as {sectors}.",
        f"In sectors like {sectors}, {investor_name} has made notable {stage} investments in companies such as {top_10_investee}.",
        f"Top companies such as {top_10_investee} have seen investments from {investor_name}, who targets {stage} investments in sectors like {sectors}.",
        f"With a focus on {stage} investments, {investor_name} has invested in notable companies such as {top_10_investee} in sectors like {sectors}."
    ]
    
    if stage == 'Null':
        description = random.choice(no_stage_formats)
    else:
        description = random.choice(with_stage_format)
    
    return description
deal_query = """
    select * from c
"""
deal_items = fetch_data_from_cosmos('Deal-Id', deal_query)
df_deal = pd.DataFrame(deal_items)

df_deal['Series_Stage'] = df_deal['Corrected_Series'].apply(map_series_to_stage)

df_deal['Main_Sector'] = df_deal['All_Sectors'].str.split('#').str[0].str.upper()
df_deal['published_date'] = pd.to_datetime(df_deal['published_date'])
print("Description Created")
import datetime
today = datetime.date.today()
up_to_day = today - datetime.timedelta(days=10000)
strtoday =  str(today)
up_to_day_ago = str(up_to_day)
 
latest_deals = df_deal[(df_deal['published_date'] >= up_to_day_ago) & (df_deal['published_date'] <= strtoday)].reset_index(drop=True)
inv_deal_ids = latest_deals['id'].to_list()

investor_query = f"SELECT c.Investor, c.id, c.Investor_Deal_Ids, c.Investor_Bio FROM c "
investor_items = fetch_data_from_cosmos('Investor-Id', investor_query)
df = pd.DataFrame(investor_items)

df=df[df['Investor_Bio'].isnull()]
print(df.shape)

df['description'] = df.apply(lambda row: generate_description(row, df_deal), axis=1)

# # Example: print descriptions
# for i, desc in enumerate(df['description'].head(10)):
#     print(f"{i+1}. {desc}")

################################### INITIALIZING MODEL ##################################

from transformers import AutoTokenizer, AutoModelForCausalLM
 
# Initialize your model and tokenizer
model_name = "TheBloke/Mistral-7B-OpenOrca-GPTQ"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    trust_remote_code=False,
    revision="main"
)
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
 
# Function to generate summary using the model
def gen_sum(context):
    prompt = f"Generate a relevant investor insight in a paragraph incorporating the provided detail: {context}"
    prompt_template = f'''
user
    {prompt}
assistant
    '''
    input_ids = tokenizer(prompt_template, return_tensors='pt').input_ids.cuda()
    try:
        # Generating output
        output = model.generate(inputs=input_ids, temperature=0.7, do_sample=True, top_p=0.95, top_k=40, max_new_tokens=512)
        raw = tokenizer.decode(output[0])
        text_after_assistant = raw.split("assistant", 1)[1].strip()
        generated_summary = text_after_assistant.split('<')[0]
        return generated_summary
    except Exception as e:
        print('ERROR : ', e)
        return 'NaN'

# Apply the model to each row in the 'description' column
df['Investor_Bio_New'] = df['description'].apply(lambda x: gen_sum(x) if pd.notna(x) else 'NaN')

    
