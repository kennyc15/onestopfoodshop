# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 14:50:15 2024

@author: cckk4
"""

import runFunctions
import cgitb 
cgitb.enable()
import openai 
import functionFile


data = runFunctions.run()

with open('mealplan.txt', 'w') as f:
    for recipe in data:
        f.write(recipe)



openai.api_key = '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'
 
 # Extract values from the given row
'''
 # Construct prompt 
prompt = f"""Create a recipe with sweetcorn, spring onions and
      ground beef as protein.
     Do not use any other fresh vegetables or proteins.
     You may use pantry items such as spices, sauces, and others that do not expire.
     Do not print measurements for ingredients_list.
     """



 # Call API 
response = openai.ChatCompletion.create(
     model="gpt-3.5-turbo-0125",
     messages=[
         {"role": "system", "content": "You are a helpful assistant."},
         {"role": "user", "content": prompt},
     ],
     max_tokens=1200  # Adjust as needed
 )
 
 # Extract the generated recipe and replace newline characters
generated_recipe = functionFile.replace_newlines(response['choices'][0]['message']['content'])
generated_recipe


with open('nobaseprotein.txt', 'a') as f:
        f.write(generated_recipe)
        '''