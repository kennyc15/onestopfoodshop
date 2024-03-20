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
        dietaryPreferences = request.form.get('dietary-preferences', "")
        allergies = request.form.get('allergies', "")
        dislikes = request.form.get('dislikes', "")
        days = request.form.get('planning-days')
        
        # Error handling for days
        try:
            days = int(days)
            if not 3 <= days <= 7:
                raise ValueError("Planning days must be between 3 and 7")
        except ValueError:
            return "Invalid input for planning days. Please enter a number between 3 and 7."
        
        # Here you can call your Python function and pass the variables
        # For example: process_preferences(dietaryPreferences, allergies, dislikes, days)
        sheets = SQLConnection.loadData()
        data = SQLConnection.generateMealPlan(sheets, dietaryPreferences, allergies, dislikes, days)
        Website.website(data)
        
        return render_template('website.html', data=data)
    # Display the form initially
    form = Website.htmlForm()
    return render_template_string(form)


if __name__ == '__main__':
    app.run(debug=True)
