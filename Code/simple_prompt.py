import itertools
import openai
import pandas as pd

openai.api_key = "insert key"

def generate_prompts():
    # Read the data from the spreadsheet
    df = pd.read_excel('spreadsheet.xlsx')

    all_prompts = df['Prompts'].tolist()
    prompts = [element for element in all_prompts if str(element) != "nan"]
    print("prompts: ", prompts)
    return prompts

#use this command if calling from GPT-4
def send_prompt4(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return response['choices'][0]['message']['content']

#use this command if calling from GPT-3.5
def send_prompt3(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            # {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI, based on the GPT-3.5 architecture. Knowledge cutoff: 2021-09 Current date: 2023-09-05"},
            {"role": "user", "content": prompt},
        ]
    )
    return response['choices'][0]['message']['content']

# Create a new DataFrame to store the answers
df_answers = pd.DataFrame(columns=['Prompt', 'Answer'])

# Generate prompts, send them, and record the answers
prompt_data = generate_prompts()

# Variable representing the # of iterations needed on the prompt.
multi = 60

while multi != 0:
    multi -= 1
    for prompt in prompt_data:
        print("current prompt: ", prompt)
        response = send_prompt3(prompt)
        
        # Create a new DataFrame with the row data
        row_data = {
            'Prompt': prompt,
            'Answer': response
        }
        new_row = pd.DataFrame(row_data, index=[0])

        # Concatenate the new row DataFrame with df_answers
        df_answers = pd.concat([df_answers, new_row], ignore_index=True)

# Save the DataFrame to a new sheet in the same spreadsheet file
with pd.ExcelWriter('final_identity_responses.xlsx', mode='a', engine='openpyxl') as writer:
    df_answers.to_excel(writer, sheet_name='last stragglers', index=False)