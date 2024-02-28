# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 17:58:54 2024

@author: cckk4
"""
from flask import Flask, request, render_template, render_template_string
import openai
import SQLConnection
import Website

openai.api_key = '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'
 
app = Flask(__name__)
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
        data = SQLConnection.run(dietary_preferences, allergies, dislikes, planning_days)
        Website.website((data))
        
        return render_template('website.html', data=data)
    # Display the form initially
    form = Website.htmlForm()
    return render_template_string(form)

if __name__ == '__main__':
    app.run(debug=True)
