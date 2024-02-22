# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 14:59:32 2024

@author: cckk4
"""

import random
import pandas as pd
import numpy as np
import math
import openai
from fractions import Fraction
import json



def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)



# Picking the Protein Sample 
# Returns the IDs of chosen proteins
# Considers the number of days in plan

# Parameters: Main ingredient sheet, number of days in plan
# CONSIDERATIONS: update ingredient sheet for allergies etc -> new function
#                   make use of frequency column


def chooseProteins(ingredients_sheet, days_in_plan):
    num_proteins = math.floor(days_in_plan / 2)

    while True:
        proteins = ingredients_sheet[ingredients_sheet['Macro'] == 'P']
        proteins = proteins[proteins['meals'] <= days_in_plan]
        
        if proteins.empty:
            # Handle the case where there are no suitable proteins
            return None

        # Calculate probabilities based on 'Frequency' column
        probs = proteins['Frequency'] / proteins['Frequency'].sum()

        # Adjusting the probability distribution to reflect 'meals' constraints
        valid_mask = proteins['meals'] <= days_in_plan
        valid_probs = np.where(valid_mask, probs, 0)
        valid_probs /= valid_probs.sum()

        # Randomly sample protein IDs based on adjusted probabilities
        protein_sample = np.random.choice(proteins['ID'], size=num_proteins, replace=False, p=valid_probs)

        # Check if the sum of 'meals' for chosen proteins is equal to days_in_plan
        if proteins.loc[proteins['ID'].isin(protein_sample), 'meals'].sum() == days_in_plan:
            return protein_sample
          
        
# Function to choose a base and get the corresponding Dish ID for the protein and base
# Retuns two lists of equal length
# 1st list = Dish ids 
# 2nd list = Chosen corresponding bases for protein-base pairs
# Ensures that protein-base pair is possible
# Varies the base chose for given protein to increase variety of meals

# Parameters: Sample of protein indices, meal_type_classification_table

def getDishIndices(proteinIndicesList, proteinDishDataframe):
    # Initialize empty dictionaries to track used base IDs for each protein
    used_base_ids = {protein_id: set() for protein_id in proteinIndicesList}

    # Initialize lists to store Dish_ID and Base_ID values
    dish_ids_list = []
    base_ids_list = []

    for protein_id_to_lookup in proteinIndicesList:
        bool_value = True

        while bool_value:
            # Generate a random Base ID between 1 and 6
            available_base_ids = set(range(1, 7)) - used_base_ids[protein_id_to_lookup]
            if not available_base_ids:
                # If all bases have been used for this protein, reset the set
                used_base_ids[protein_id_to_lookup] = set()

            base_id_to_lookup = np.random.choice(list(available_base_ids))

            # Look up the combination of Protein_ID and Base_ID
            result = proteinDishDataframe.loc[
                (proteinDishDataframe['Protein_ID'] == protein_id_to_lookup)
                & (proteinDishDataframe['Base_ID'] == base_id_to_lookup),
                'Dish_ID'
            ]

            # Check if the combination exists
            if not result.empty:
                dish_id = result.iloc[0]
                dish_ids_list.append(dish_id)  # Append the dish_id to the list
                base_ids_list.append(base_id_to_lookup)
                used_base_ids[protein_id_to_lookup].add(base_id_to_lookup)  # Update used base IDs
                bool_value = False  # Exit the while loop if a valid combination is found
            else:
                bool_value = True

    # Now dish_ids_list contains all the Dish_ID values
    return dish_ids_list, base_ids_list



# Function to get the number of meals that will have a protein
# Cannot be greater than number of days in the plan
# Can be less than days in plan

# Parameters: Sample of protein indices, days in plan, ingredients Sheet

def getNumberMeals(indices, daysInPlan, ingredientsSheet):
    totalNumMeals = np.sum(ingredientsSheet.loc[ingredientsSheet['ID'].isin(indices), 'meals'])
    return totalNumMeals



# Function to list the proteins based on how many meals they are included in
# e.g. if index 26 has meals = 2.0, the list returned is [26, 26]

def duplicatedList(ingMealCounter, totalPortions):
    v = []
    bool_val = False

    while not bool_val:
        id_list = ingMealCounter['ID'].tolist()
        x = random.choice(id_list)
        
        matching_indices = ingMealCounter.index[ingMealCounter['ID'] == x]
        
        if len(matching_indices) > 0:
            index_x = matching_indices[0]
        
        index_x = ingMealCounter.index[ingMealCounter['ID'] == x][0]
        if ingMealCounter.at[index_x, 'meals'] != 0:
            v.append(x)
            ingMealCounter.at[index_x, 'meals'] -= 1
            ingMealCounter = ingMealCounter[ingMealCounter['ID'] != 0]
            
            if len(v) == totalPortions:
                bool_val = True

    return v



# Returns a dataframe where
# Col 1 = protein indices
# Col 2 = corresponding number of meals

def getIngredientMealsDataframe(ingredientSheet, ingredientIndices):
    ingCounter = ingredientSheet[ingredientSheet['ID'].isin(ingredientIndices)][['ID', 'meals']]
    return ingCounter



# Combines the dish, base and protein selections in one dataframe

def createDishBaseProteinDataframe(dish, base, protein):
    df = pd.DataFrame({'Dish_ID': dish, 'Base_ID': base, 'Protein_ID': protein})
    return(df)



# Given the chosen dish IDs, this function scores the vegetables based on how 
# many of the dishes they can go in to by adding a creating an ingredient ID and score column in a dataframe

def calculate_veg_score(df1, df2):
        # Assuming df1 and df2 are your dataframes
        dishBaseProtein = df1
        groupingSheet = df2

        # Create a new dataframe to store the results
        result_df = pd.DataFrame(columns=['Ingredient_ID', 'Score'])

        # Loop through every dish_id in df1
        for dish_id in dishBaseProtein['Dish_ID']:
            # Find matches in Dish_ID in df2
            matches = groupingSheet.loc[groupingSheet['DishID'] == dish_id, 'IngredientID']

            # Iterate through matches and update result_df
            for ingredient_id in matches:
                if not result_df.empty and ingredient_id in result_df['Ingredient_ID'].values:
                    # Increment the score if the ingredient is already in result_df
                    result_df.loc[result_df['Ingredient_ID'] == ingredient_id, 'Score'] += 1
                else:
                    # Add the ingredient to result_df with a score of 1 if it's not already present
                    result_df = pd.concat([result_df, pd.DataFrame({'Ingredient_ID': [ingredient_id], 'Score': [1]})], ignore_index=True)

        # Return the final result_df
        return result_df
    


# Retunns the top scoreres from the last function
# The number of veg chosen based on daysInPlan and a margin of randomness to reflect real life recipes
# This returns IDs of vegetables that will be used in the meal plan

def top_scorers(vegScoreDataframe, daysInPlan):
    numVegUp = (3 + daysInPlan)
    numVegLow = (daysInPlan + 2)
    size=int(np.floor(np.random.uniform(numVegLow, numVegUp)))
    # Sort the DataFrame based on the 'Scoring' column in descending order
    sorted_df = vegScoreDataframe.sort_values(by='Score', ascending=False)

    # Print the top n scorers' Dish IDs
    x = sorted_df.head(size)['Ingredient_ID'].tolist()
    return x



# This function gives the vegetable combinations for recipes each day
# It makes sure that a different combination is used every day
# Ingredients in each combination are unique

'''
Sample Output: 
    
[array([81, 71,  7, 14]),
 array([81, 14,  7, 71]),
 array([71, 88,  7, 85]),
 array([88,  7, 71, 85]),
 array([14, 81,  7, 88])]

'''

def divide_strings(input_vector, x):
    # Check if the input vector has enough unique elements for division
    if len(np.unique(input_vector)) < x:
        raise ValueError("Not enough unique elements in the input vector for division.")
    
    bool_val = False
    while not bool_val:
        # Shuffle the input vector randomly
        shuffled_vector = random.sample(input_vector, len(input_vector))
        
        # Divide the shuffled vector into x non-repeating substrings
        substrings = np.array_split(shuffled_vector, x)

        # Find the maximum length among all substrings
        max_length = max(len(substring) for substring in substrings)

        # Add zeros to shorter substrings to make them equal in length
        substrings = [np.pad(substring, (0, max_length - len(substring)), 'constant') for substring in substrings]

        # Check if each substring has unique elements
        bool_val = all(len(np.unique(substring)) == len(substring) for substring in substrings)
            
    return substrings



# Function to combine veg, protein, base and dish id 
# Each row represents the combination for a given day
# ProteinID is the only column that may be left blank

'''
Sample Output: 
    Veg1  Veg2  Veg3  Veg4  Dish_ID  Base_ID  Protein_ID
0    81    71     7    14      8.0      2.0        48.0
1    81    14     7    71      6.0      4.0        27.0
2    71    88     7    85      3.0      5.0        27.0
3    88     7    71    85      4.0      6.0        48.0
4    14    81     7    88      NaN      NaN         NaN
'''

def vegBaseProteinDish(vegetablesByDay, DishBaseProteinDataframe):
    
    # Determine the maximum length of arrays in the list
    max_length = max(len(arr) for arr in vegetablesByDay)

    # Generate column names based on the maximum length
    column_names = [f'Veg{i+1}' for i in range(max_length)]

    vegDf = pd.DataFrame(vegetablesByDay, columns=column_names)

    df1 = pd.DataFrame(vegDf)
    df2 = pd.DataFrame(DishBaseProteinDataframe)

    result_df = pd.concat([df1, df2], axis=1)

    # Reorder columns to keep 'Dish_ID', 'Base_ID', and 'Protein_ID' as the last three columns
    result_columns = [col for col in result_df.columns if col not in ['Dish_ID', 'Base_ID', 'Protein_ID']] + ['Dish_ID', 'Base_ID', 'Protein_ID']
    result_df = result_df[result_columns]

    # Display the result
    return result_df



# Ensures that the dataframe has no NaN entries
# Replaces 0 entries under Base ID with random Base ID and assigns dish ID based on rules

'''
Sample Output: 
	Veg1 Veg2 Veg3 Veg4 Dish_ID Base_ID Protein_ID
0	 81	 71  	7	14 	8   	2	    48
1	 81	 14	    7	71	6	    4	    27
2	 71	 88	    7	85	3	    5	    27
3	 88	 7	   71	85	4   	6	    48
4	 14	 81	   7	88	1	    2	     0
'''

def completeDataframe(data):
    
    df = pd.DataFrame(data)

    # Replace NaN values with 0s
    df = df.fillna(0)

    # Replace 0s in 'Base_ID' with a random number between 1 and 6
    mask = (df['Dish_ID'] == 0) & (df['Base_ID'] == 0)

    # Generate random numbers between 1 and 6
    random_numbers = np.random.randint(1, 7, size=sum(mask))

    # Update 'Base_ID' with random numbers for the rows where both 'Dish_ID' and 'Base_ID' are 0
    df.loc[mask, 'Base_ID'] = random_numbers
    
    # Define rules for replacing 'Dish_ID'
    rules = {1: 12, 2: 1, 3: 2, 4: 6, 5: 3, 6: 4}

    # Apply rules to update 'Dish_ID'
    df.loc[mask, 'Dish_ID'] = df.loc[mask, 'Base_ID'].map(rules)

    # Convert columns to integers (optional, depending on your needs)
    df[['Dish_ID', 'Base_ID', 'Protein_ID']] = df[['Dish_ID', 'Base_ID', 'Protein_ID']].astype(int)

    return df



# Parameters: completed dataframe, ingredients sheet, base sheet, dish sheet
# Replaces the veg, base, protein and dish IDs with corresponding string names
# Rows of this data frame are used as input to the LLM
    

def replaceIndicesWithStrings(result_df, ingredientsSheet, basesSheet, dishSheet):
    # Convert input data to dataframes
    df_A = pd.DataFrame(ingredientsSheet)
    df_B = pd.DataFrame(basesSheet)
    df_C = pd.DataFrame(dishSheet)
    df_D = df_A
    df_check = pd.DataFrame(result_df)
    
    # Columns to be replaced for each dataframe
    columns_replace_A = df_check.columns[-1:].tolist()
    columns_replace_B = df_check.columns[-2:-1].tolist()
    columns_replace_C = df_check.columns[-3:-2].tolist()
    
    # Replace values in the specified columns for each dataframe
    for col in columns_replace_A:
        df_check[col] = df_check[col].apply(lambda x: df_A.loc[df_A['ID'] == int(x), 'Name'].values[0] if (isinstance(x, (int, float)) and x != 0 and int(x) in df_A['ID'].values) else x)

    for col in columns_replace_B:
        df_check[col] = df_check[col].apply(lambda x: df_B.loc[df_B['ID'] == int(x), 'Name'].values[0] if (isinstance(x, (int, float)) and x != 0 and int(x) in df_B['ID'].values) else x)
        
    for col in columns_replace_C:
        df_check[col] = df_check[col].map(lambda x: df_C.loc[df_C['ID'] == int(x), 'Name'].values[0] if (isinstance(x, (int, float)) and x != 0 and int(x) in df_C['ID'].values) else x)

    df_check = df_check.map(lambda x: df_D.loc[df_D['ID'] == int(x), 'Name'].values[0] if (isinstance(x, (int, float)) and x != 0 and int(x) in df_D['ID'].values) else x)
    
    return df_check


# this function gets the servings of fresh ingredients for each recipe
# it is a fraction = to 1/ meals

def getServings(proteinIDs, vegIDs, data):

    merge = proteinIDs + vegIDs
    df = pd.DataFrame(data)
    
    df['Fractions'] = df['meals'].apply(lambda x: Fraction(1, int(x)))

    # Filter rows based on the provided set of IDs
    filtered_df = df[df['ID'].isin(merge)]

    # Return the resulting DataFrame
    return filtered_df[['Name', 'Fractions']]



def replace_newlines(text):
    # Replace variations of newline characters with actual line breaks
    return text.replace("\\n", "\n").replace("\n", "\n")


def convert_recipes_to_dict(recipes_list):
    # Join the list items into a single string, assuming each item is a complete JSON object
    # and assuming they are separated in a way that needs correction for valid JSON formatting.
    formatted_str = "[" + ",".join(recipes_list) + "]"
    
    try:
        # Load the string as a JSON array (list of dictionaries in Python)
        recipes_list = json.loads(formatted_str)
        
        # Convert the list into a dictionary with `recipe_title` as keys
        recipes_dict = {recipe["recipe_title"]: recipe for recipe in recipes_list}
        return recipes_dict
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    

def convert_list_to_recipe_dict(recipe_list):
    recipes_dict = {}
    for recipe_str in recipe_list:
        # Parse each string as a JSON object
        recipe = json.loads(recipe_str)
        # Add the recipe to the dictionary, using the title as the key
        recipes_dict[recipe["recipe_title"]] = recipe
    return recipes_dict
    


def generateRecipe(api_key, row, diet, allergen):
    # Set API key
    openai.api_key = api_key
    
    # Extract values from the given row
    num_veg_cols = len(row) - 3
    veg_columns = [f'Veg{i}' for i in range(1, num_veg_cols + 1)]

    # Extract values from the given row
    vegetables = [row[col] for col in veg_columns]
    protein = row['Protein_ID']
    base = row['Base_ID']
    dish_id = row['Dish_ID']
    
    # Construct prompt 
    prompt = f"""Create a recipe with {', '.join(map(str, vegetables))} as vegetables,
        {protein} as protein, and {base} as the base.
        If there are allergens or dietary requirements, they are; {diet, allergen}
        Do not use any other fresh vegetables or proteins.
        You may use pantry items such as spices, sauces, and others that do not expire.
        Give the recipe a creative, fun name relevant for a {dish_id} dish.
        Do not print measurements for ingredients_list.
        Return each recipe as a json objects with four keys: recipe_title, ingredients
        instructions, notes. 
        
        Example: 
          {{
            "recipe_title": "Tomato Tango Pasta",
            "ingredients": [
                "Pasta",
                "Sundried tomatoes",
                "Cherry tomatoes",
                "Red onion",
                "Arugula",
                "Kidney beans",
                "Olive oil",
                "Garlic",
                "Red pepper flakes",
                "Salt",
                "Black pepper"
            ],
            "instructions": [
                "Cook the pasta according to package instructions, then drain and set aside.",
                "In a large pan, heat olive oil over medium heat. Add minced garlic and red pepper flakes, and sauté until fragrant.",
                "Add sliced red onion and sauté until translucent. Then add the cherry tomatoes and sundried tomatoes, cook for a few minutes until softened.",
                "Add the kidney beans and cooked pasta to the pan. Season with salt and black pepper, then toss everything together until well combined.",
                "Turn off the heat and stir in the arugula until it wilts slightly.",
                "Serve the Tomato Tango Pasta hot, garnished with some extra arugula leaves."
            ],
            "notes": "Feel free to top with some grated Parmesan cheese or a drizzle of balsamic glaze for extra flavor."
          }}
          """



    # Call API 
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125", temperature = 0.5,
        messages=[
            {"role": "system", "content": "You are a recipe creator."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1200,  # Adjust as needed
    )
    
    # Extract the generated recipe and replace newline characters
    generated_recipe = replace_newlines(response['choices'][0]['message']['content'])
   
    return generated_recipe



def formatJson(recipe_list, api_key):
    # Set API key
    openai.api_key = api_key
    
    recipe_list_str = str(recipe_list) if recipe_list else '[]'

    prompt = f'''
        Ensure that each individual recipe in the list below is in proper JSON format so that it can be parsed into a dictionary:
        
        {recipe_list_str}
        
        The four keys are: recipe_title, ingredients, instructions, notes. 
        Keep these points in mind:
        - Missing Quotes: Every string value and key in JSON must be enclosed in double quotes (""). Single quotes (') are not valid.
        - Trailing Commas: JSON does not allow trailing commas. For example, in an object or array, having a comma after the last element can cause parsing to fail.
        - Incorrect Brackets: Ensure that all objects (curly brackets) and arrays (square brackets) are correctly opened and closed.
        - Empty Values: JSON parsers expect every key to have a value. Ensure there are no keys without values.
        
        This ensures that your data is correctly structured for JSON parsing, which is critical for further processing or analysis.
        Return as a list of Json objects. 
    '''

    # Call API 
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125", temperature = 0.5,
        messages=[
            {"role": "system", "content": "You are a json format expert."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,  # Adjust as needed
    )
    y = response['choices'][0]['message']['content']
    return y
