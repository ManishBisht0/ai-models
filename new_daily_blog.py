from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_name_or_path = "TheBloke/Mistral-7B-OpenOrca-GPTQ"
model = AutoModelForCausalLM.from_pretrained(model_name_or_path,
                                             device_map="auto",
                                             trust_remote_code=False,
                                             revision="main")

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)
print('---------------------------------- TRANFORMER MODEL LOADED SUCCESFULLY', '-'*30)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=1024, #USED 1200, 1300 EARLIER
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

# INTRO
deal_quantity = 15
for i in range(0, df.shape[0], deal_quantity):
    raw_summaries = "\n".join(df["summary_of_article"][i:i+deal_quantity])
    prompt = f""" Generate a concise statement in 2 lines summarizing the impact of recent funding rounds on the startup ecosystem, only mention the top three sectors.
                  Emphasize their contribution to innovation and growth.
                  Only consider the data provided.

    data = {raw_summaries}
    """
    intro = invoke(prompt)
df["intro_text"] = intro
print('--------------------------------------- INTRODUCTION GENERATED SUCCESFULLY', '-'*30)


# SUMMARIES
generated_summaries = []
for i in range(df.shape[0]):
    raw_summaries = df["summary_of_article"][i]
    prompt = f""" You have to write a business article based on the instructions provided.
                  Generate a rephrased summary of the funding rounds for each startup.
                  Ensure that in summary the startup is given a separate section and output is generated in a paragraph format.
                  The article should only contain data provided to you.

    data = {raw_summaries}
    """
    output = invoke(prompt)
    generated_summaries.append(output)
df["generated_summary"] = generated_summaries
print('---------------------------------------- SUMMARIES GENERATED SUCCESFULLY: ',len(generated_summaries), '-'*30)


# OUTRO
deal_quantity = 15
for i in range(0, df.shape[0], deal_quantity):
    raw_summaries = "\n".join(df["summary_of_article"][i:i+deal_quantity])
    prompt = f""" Write an engaging one line closing paragraph for an article.
                  Do not mentioning specific companies or funding amounts.
                  Consider the data provided for reference.

    data = {raw_summaries}
    """
    output = invoke(prompt)
    print(output)
df['outro_text'] = output
print('------------------------------------------ CONCLUSION GENERATED SUCCESFULLY', '-'*30)

# CLEANING FOR IRRELEVANT OUTPUT
df['length'] = df['generated_summary'].apply(lambda x: len(x))
