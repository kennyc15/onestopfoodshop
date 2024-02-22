# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 17:58:54 2024

@author: cckk4
"""

import runFunctions
import mainFile
from flask import Flask, request, render_template_string
from flask import Flask, request, render_template
import json
import functionFile
import openai

app = Flask(__name__)

openai.api_key = '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'
 
# HTML form
HTML_FORM = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Submit Your Preferences</title>
</head>
<body>
<form method="post">
  <label for="dietary-preferences">Enter your dietary preferences:</label>
  <input type="text" id="dietary-preferences" name="dietary-preferences"><br>
  <label for="allergies">Enter any allergies you have:</label>
  <input type="text" id="allergies" name="allergies"><br>
  <label for="dislikes">Enter any food you dislike:</label>
  <input type="text" id="dislikes" name="dislikes"><br>
  <label for="planning-days">Enter the number of days you would like to plan for (3-7):</label>
  <input type="text" id="planning-days" name="planning-days"><br>
  <input type="submit" value="Submit">
</form>
</body>
</html>
'''


@app.route('/', methods=['GET', 'POST'])

def form():
    if request.method == 'POST':
        # Process form data
        dietary_preferences = request.form.get('dietary-preferences', "")
        allergies = request.form.get('allergies', "")
        dislikes = request.form.get('dislikes', "")
        planning_days = request.form.get('planning-days')
        
        # Here you can call your Python function and pass the variables
        # For example: process_preferences(dietary_preferences, allergies, dislikes, planning_days)
        data = runFunctions.run(dietary_preferences, allergies, dislikes, planning_days)
        mainFile.website((data))
        
        return render_template('website.html', data=data)
    # Display the form initially
    return render_template_string(HTML_FORM)


if __name__ == '__main__':
    app.run(debug=True)

'''
data = runFunctions.run("","","",3)
print(data)
mainFile.website(data)
'''