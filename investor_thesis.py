import numpy as np
import random
import re
from azure.cosmos import CosmosClient
import datetime
import pytz
import pandas as pd
import uuid
import math
import json
from datetime import datetime
 
# Create a directory for the model
# !mkdir Mistral-7B-OpenOrca-GPTQ
# !pip install azure-cosmos
## Download the model using huggingface-cli
# !huggingface-cli download TheBloke/Mistral-7B-OpenOrca-GPTQ --local-dir Mistral-7B-OpenOrca-GPTQ --local-dir-use-symlinks False
# !pip uninstall pyarrow
# !pip install pyarrow
# !pip3 install huggingface-hub
# !pip3 install transformers optimum
# !pip3 install auto-gptq --extra-index-url https://huggingface.github.io/autogptq-index/whl/cu118/  # Use cu117 if on CUDA 11.

 
endpoint= "entre your endpoint here"
key="please enter your key here"
 
client = CosmosClient(endpoint, key)
db = client.get_database_client("db")
cn=db.get_container_client('continer')
query="select * from c"
items=cn.query_items(query,enable_cross_partition_query=True)
items_list=list(items)
df = pd.DataFrame(items_list)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% LOADING MISTRAL LLM MODEL %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
 
model_name_or_path = "TheBloke/Mistral-7B-OpenOrca-GPTQ"
model = AutoModelForCausalLM.from_pretrained(model_name_or_path,
                                             device_map="auto",
                                             trust_remote_code=False,
                                             revision="main")
 
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)
print('TRANFORMER MODEL LOADED SUCCESFULLY')
 
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=1200, #USED 1200, 1300 EARLIER
    do_sample=True,
    temperature=0.01,
    top_p=0.95,
    top_k=40,
    repetition_penalty=1.1
)
 
def invoke(prompt) -> str:
    prompt_template=f'''
    <|im_start|>user
    {prompt}<|im_end|>
    <|im_start|>assistant
    '''
 
    raw=(pipe(prompt_template)[0]['generated_text'])
    # extracting only generated output
    output = raw.split("<|im_start|>assistant", 1)[1].strip()
    return output
 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% GENERATING OUTPUT %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

generated_summaries = []
investor_thesis = []
title = []
for i in range(df.shape[0]):
 
    investor_name = df['Investor'][i]
    invest_bio = df['Investor_Bio'][i]
    prompt = f"""Write a 400 words detailed rephrased summary about the investor: {investor_name} using the data provided. Talk in detail about the various sectors invested in by the investor: {investor_name}. Write in detail about the impact of the investments in growth and development of these sectors. Do not use bullet points.
              Only consider the data provided.
 
    data = {invest_bio}
    """
    output1 = invoke(prompt)
    generated_summaries.append(output1)
 
    prompt = f""" Write a paragraph mentioning what type of companies should approach {investor_name} for raising funds. Do not use bullet points. Only consider the data provided.
   
    data = {invest_bio}
 """
    output2 = invoke(prompt)
    investor_thesis.append(output2)
 
    prompt = f''' Generate a concise 1 line title for an article using the data provided for investor:{investor_name}. Only use the data provided.
     
      data = {invest_bio} '''
 
    output3 = invoke(prompt)
    title.append(output3)
 
df["Investor_thesis"] = investor_thesis
df['title'] = title
print('Investor thesis GENERATED SUCCESFULLY: ',len(investor_thesis))
 
df["generated_investor_summary"] = generated_summaries
print('SUMMARIES GENERATED SUCCESFULLY: ',len(generated_summaries))
 
inv1=df[['id', 'Investor', 'Investor_Bio',
       'Investor_thesis', 'title', 'generated_investor_summary']]
inv1.rename(columns={'id':'Investor_Id',
                    'Investor_thesis':'Investor_Thesis','title':'Title','generated_investor_summary':'Summary'},inplace=True)
 
def remove_quotes(s):
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s
inv1['Title'] = inv1['Title'].apply(remove_quotes)
 
inv1_new = inv1.drop_duplicates(subset=['Investor_Id']).reset_index(drop=True)
 
inv1_new['Investor_Info'] = inv1_new.apply(lambda x: {
    'Investor':x['Investor'],
    'Investor_Bio': x['Investor_Bio'],
    'Investor_Thesis': x['Investor_Thesis'],
    'Title': x['Title'],
    'Summary': x['Summary']}, axis=1)
