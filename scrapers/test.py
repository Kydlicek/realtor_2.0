from utils.prompt_ai import make_prompt

prompt='how much is 1+1?'
purpose='u are a math expert return only the answer'

response=make_prompt(prompt,purpose)
print(response)
