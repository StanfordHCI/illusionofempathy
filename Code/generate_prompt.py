import itertools
import openai
import pandas as pd

openai.api_key = "insert key"

def generate_prompts():
    # Read the data from the excel spreadsheet; to see how it should be formatted, see the csv file
    df = pd.read_excel('prompt_options.xlsx')

    all_templates = df['Templates'].tolist()
    templates = [element for element in all_templates if str(element) != "nan"]
    print("templates: ", templates)
    
    # Potential adjectives/identities
    substitutions = {}
    for col in df.columns:
        if col != 'Templates' and col != 'Level of Privilege' and col != 'Ignore' and pd.notnull(col):
            substitutions[col] = df[col].dropna().tolist()
    print("substitutions: ", substitutions)

    # Adjective combinations, computationally expensive
    combinations = {}
    for count in range(1, 3):
        combinations[count] = []
        for combination in itertools.combinations_with_replacement(substitutions.items(), count):
            values = [item for _, item in combination]
            combinations[count].extend(itertools.product(*values))
    # print("combinations: ", combinations)

    # Generate prompts for each template
    prompts = []
    for template in templates:
        num_placeholders = template.count('{}')

        if num_placeholders in combinations:    
            for combination in combinations[num_placeholders]:
                prompt = template.format(*combination)

                prompt_info = {
                    'prompt': prompt,
                    'substitutions': combination,
                }
                prompts.append(prompt_info)
    return prompts

def send_prompt(prompt):
    response = openai.ChatCompletion.create(
        # Change the model to "gpt-4" to use gpt-4
        model="gpt-3.5-turbo",

        # To add a preprompt, add a message with "role": "system" or include the pre-prompt in the user prompt
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return response['choices'][0]['message']['content']

# Create a new DataFrame to store the answers
df_answers = pd.DataFrame(columns=['Prompt', 'Substitutions', 'Answer'])

# Generate prompts, send them, and record the answers
prompts = generate_prompts()

# Variable for # of times to generate responses
multi = 1

while multi != 0:
    multi -= 1
    for prompt_info in prompts:

        response = send_prompt(prompt_info['prompt'])

        # Create a new DataFrame with the row data
        row_data = {
            'Prompt': prompt_info['prompt'],
            'Substitutions': [prompt_info['substitutions']],
            'Answer': response
        }
        new_row = pd.DataFrame(row_data)
        print("substutions: ", prompt_info['substitutions'])

        # Concatenate the new row DataFrame with df_answers
        df_answers = pd.concat([df_answers, new_row], ignore_index=True)

# Save the DataFrame to a new sheet; spreadsheet must already exist
with pd.ExcelWriter('example_results.xlsx', mode='a', engine='openpyxl') as writer:
    df_answers.to_excel(writer, sheet_name='sheet 1', index=False)