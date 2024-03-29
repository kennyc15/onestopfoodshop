# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 14:50:15 2024

@author: cckk4
"""

import cgitb 
cgitb.enable()
import json
import SQLConnection

def website(data):
    
    sheets = SQLConnection.loadData()
    ingredientsSheet = sheets['ingredientsSheet']
    
    with open('templates/website.html', 'w', encoding='utf-8') as file:
        # Start of the HTML document
        file.write("<!DOCTYPE html>\n")
        file.write("<html lang='en'>\n")
        file.write("<head>\n")
        file.write("<meta charset='UTF-8'>\n")
        file.write("<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
        file.write("<title>One Stop Food Shop</title>\n")
        file.write("<style>\n")
        file.write("  body { background-color:#D0FBCD; }\n")
        file.write("  .margin-container { margin: auto; max-width: 1200px; padding: 20px; }\n")
        file.write("</style>\n")
        file.write("</head>\n")
        file.write("<body>\n")
        file.write("<div class='margin-container'>\n")

        unique_ingredients = set()
        
        # Assuming 'data' is your input data structure
        if isinstance(data, dict):
            recipes = [data]  # Wrap it in a list to standardize the loop below
        elif isinstance(data, list):
            recipes = data
        else:
            raise ValueError("Unsupported data type for 'data'. Expected a list or a dictionary.")
        
        i = 0
        for recipe_str in recipes:
            if not isinstance(recipe_str, str):
                print(f"Expected a string, got {type(recipe_str)}")
                continue  # Skip non-string items
            try:
                recipe = json.loads(recipe_str)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                continue
            i += 1
            file.write(f"<h1>Day {i}</h1>\n")
            file.write("<h2>Recipe Title</h2>\n")
            file.write(f"<div>{recipe.get('recipe_title', 'No Title')}</div>\n")
            file.write("<h2>Ingredients</h2>\n")
            file.write("<ul>\n")
            for ingredient in recipe.get('ingredients', []):
                file.write(f"<li>{ingredient}</li>\n")
                unique_ingredients.add(ingredient)  # Add ingredient to the set
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
            file.write("<hr>\n")
               
            # Print the 'Shopping List' before ending the document
        file.write("<h2>Shopping List</h2>\n")
        file.write("<ul>\n")
        for ingredient in sorted(unique_ingredients):  # Sort ingredients for easier reading
            file.write(f"<li>{ingredient}</li>\n")
        file.write("</ul>\n")
        file.write("<h2>Measurements</h2>\n")
        file.write("<table border='1'>\n")  # Simple table with border; style as needed
        file.write("<tr><th>Item</th><th>Quantity</th><th>Fraction used in recipe</th></tr>\n")  # Table headers

            # Proper indentation starts here
      
        for ingredient_name in sorted(unique_ingredients):
            filtered_df = ingredientsSheet[ingredientsSheet['Name'] == ingredient_name.lower()]
            print(ingredient_name.lower())
          #  print(ingredientsSheet['Name'])
            #print(ingredientsSheet[ingredientsSheet['Name']])
            if not filtered_df.empty:
                ingredient_row = filtered_df.iloc[0]
                shop_quantity = ingredient_row['ShopQuantity']
                meals = ingredient_row['meals']
                if meals > 0:
                    fraction_used = 1 / meals
                    fraction_display = f"{fraction_used:.2f}"  # Format fraction for display
                else:
                    fraction_display = "N/A"  # Handle cases where 'meals' might be zero or not applicable
                
                    # Write the table row for the ingredient
                file.write(f"<tr><td>{ingredient_name}</td><td>{shop_quantity}</td><td>{fraction_display}</td></tr>\n")
            
            # Close the table HTML tag
        file.write("</table>\n")
            
            # End of the body and HTML document
        file.write("</body>\n")
        file.write("</html>\n")

                
            
        
def htmlForm():
    HTML_FORM='''
       <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>Submit Your Preferences</title>
    <style>
      /* Your existing styles */
      body {
        background-color: #D0FBCD; /* Set the background color */
      }
      .container {
        display: flex; /* Enable flexbox */
        justify-content: center; /* Center children horizontally */
        align-items: start; /* Align children at the start of the cross axis */
      }
      form {
         max-width: 1000px; /* Allow the form to grow */
        padding: 30px; /* Add some padding inside the form */
        border: 2px solid green; /* Add a green border around the form */
        margin-right: 20px; /* Add some space between the form and the image */
        margin-top: 130px;
      }
      label, input {
        display: block; /* Make label and input take the full width */
        margin-bottom: 10px; /* Add some space below each input field */
      }
      input[type="submit"] {
        width: auto; /* Do not stretch the submit button */
        margin-top: 20px; /* Add some space above the submit button */
      }
      .form-image, .form-iframe {
        flex: 1; /* Allow the image and iframe to grow */
        max-width: 500px; 
        margin-top: 100px;
      }
      img, iframe {
        max-width: 100%; /* Make image and iframe fully responsive */
        height: auto; /* Maintain aspect ratio for images */
      }
    </style>
    </head>
    <body>
    <div class="container">
      <form id="preferenceForm" method="post">
        <!-- Your existing form fields -->
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
      <!-- Your image div -->
      <div class="form-image">
        <img src="https://framerusercontent.com/images/CoMwGenhYzzdwcUoeo2Avl2GE.png">
      </div>
    </div>
    
    <script>
    document.getElementById('preferenceForm').addEventListener('submit', function(event) {
        const planningDaysInput = document.getElementById('planning-days');
        const planningDaysValue = parseInt(planningDaysInput.value, 10);
        const validDays = [3, 4, 5, 6, 7];
    
        if (!validDays.includes(planningDaysValue)) {
            // Show an alert if the input value is not in the validDays array
            alert('Please enter a number of days between 3 and 7.');
            event.preventDefault(); // Prevent form from submitting
        }
        // If validation passes, the form will submit normally
    });
    </script>
    
    </body>
    </html>
    
        '''
    return HTML_FORM
