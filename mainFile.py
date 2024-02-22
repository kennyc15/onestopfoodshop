# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 14:50:15 2024

@author: cckk4
"""

import cgitb 
cgitb.enable()
import json


def website(data):
    with open('website.html', 'w') as file:
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
            try:
                recipe = json.loads(recipe_str)  # Parse the JSON string into a dictionary
                # Now you can work with `recipe` as a dictionary
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
            # Assuming each 'recipe' is a dictionary with the keys: 'recipe_title', 'ingredients', 'instructions', and 'notes'
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

        # Adding JavaScript for button functionality
        file.write("</div>\n")
        file.write("<script>\n")
        file.write("document.getElementById('runFunction').addEventListener('click', function() {\n")
        file.write("  fetch('/path-to-your-function-endpoint')\n")
        file.write("    .then(response => response.json())\n")
        file.write("    .then(data => {\n")
        file.write("      console.log(data); // For demonstration\n")
        file.write("      // Update HTML based on 'data'\n")
        file.write("    })\n")
        file.write("    .catch(error => console.error('Error:', error));\n")
        file.write("});\n")
        file.write("</script>\n")

        # End of the body and HTML document
        file.write("</body>\n")
        file.write("</html>\n")
