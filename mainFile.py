# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 14:50:15 2024

@author: cckk4
"""

import cgitb 
cgitb.enable()
import json
import runFunctions
from flask import Flask, request, render_template_string
from flask import Flask, request, render_template


def website(data):
    with open('templates/website.html', 'w', encoding='utf-8') as file:
        # Start of the HTML document
        file.write("<!DOCTYPE html>\n")
        file.write("<html lang='en'>\n")
        file.write("<head>\n")
        file.write("<meta charset='UTF-8'>\n")
        file.write("<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
        file.write("<title>One Stop Food Shop</title>\n")
        file.write("<style>\n")
        file.write("  body { background-color: palegreen; }\n")
        file.write("  .margin-container { margin: auto; max-width: 1200px; padding: 20px; }\n")
        file.write("</style>\n")
        file.write("</head>\n")
        file.write("<body>\n")
        file.write("<div class='margin-container'>\n")

        # Check if data is a list or a dictionary
        if isinstance(data, dict):
            recipes = [data]  # Wrap it in a list to standardize the loop below
        elif isinstance(data, list):
            recipes = data
        else:
            raise ValueError("Unsupported data type for 'data'. Expected a list or a dictionary.")

        for recipe_str in recipes:
            print(repr(recipe_str))  # Use repr() to reveal hidden characters
            if not isinstance(recipe_str, str):
                print(f"Expected a string, got {type(recipe_str)}")
                continue  # Skip non-string items
            try:
                recipe = json.loads(recipe_str)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                continue
            file.write("<h1>Recipe Title</h1>\n")
            file.write(f"<div>{recipe.get('recipe_title', 'No Title')}</div>\n")
            file.write("<h1>Ingredients</h1>\n")
            file.write("<ul>\n")
            for ingredient in recipe.get('ingredients', []):
                file.write(f"<li>{ingredient}</li>\n")
            file.write("</ul>\n")
            file.write("<h2>Instructions</h2>\n")
            file.write("<ul>\n")
            for instruction in recipe.get('instructions', []):
                file.write(f"<li>{instruction}</li>\n")
            file.write("</ul>\n")
            file.write("<h2>Notes</h2>\n")
            file.write("<ul>\n")
            notes = recipe.get('notes', [])
            if isinstance(notes, str):
                file.write(f"<li>{notes}</li>\n")
            else:
                for note in notes:
                    file.write(f"<li>{note}</li>\n")
            file.write("</ul>\n")

        # End of the body and HTML document
        file.write("</body>\n")
        file.write("</html>\n")

    

