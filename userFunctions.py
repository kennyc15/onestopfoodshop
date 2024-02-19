# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 20:00:04 2024

@author: cckk4
"""


# Removes the ingredients that contain user allergens

def removeAllergensByID(allergies, allergenSheet):
    allergies = [allergies]
    allergenSheet['Name'] = allergenSheet['Name'].str.strip()

    # Now you can proceed with your filtering
    filtered_df = allergenSheet[allergenSheet['Name'].isin(allergies)]

    # Check if the filtered DataFrame is not empty and retrieve the value
    if not filtered_df.empty:
        retrieved_value = filtered_df['ID'].iloc[0]
        return int(retrieved_value)
    else:
        return "No matching row found"
    
    
    
# Removes ingredients that are unsuitable for given dietary preference
# Need to update this for the bases pasta/ noodles/ bread

def removeDietsByID(dietaryPreferences, dietSheet):
    dietaryPreferences = [dietaryPreferences]
    dietSheet['Name'] = dietSheet['Name'].str.strip()

    # Now you can proceed with your filtering
    filtered_df = dietSheet[dietSheet['Name'].isin(dietaryPreferences)]

    # Check if the filtered DataFrame is not empty and retrieve the value
    if not filtered_df.empty:
        retrieved_value = filtered_df['ID'].iloc[0]
        return int(retrieved_value)
    else:
        return "No matching row found"
        


# Filter ingredients from the main ingredients sheet before creating meal plan
    
def remove_disliked_words(name, dislikes_list):
    words = name.lower().split()
    modified_words = [word for word in words if word not in dislikes_list]
    modified_name = ' '.join(modified_words)
    return modified_name


def filterIngredients(ingredientsSheet, removeDietID_str='', removeDietID_int=None, removeAllergenID_str='', removeAllergenID_int=None, dislikes=None):
    # Replace NaN with an empty string before applying str.contains()
    ingredientsSheet['Diets'] = ingredientsSheet['Diets'].fillna('')
    ingredientsSheet['Allergens'] = ingredientsSheet['Allergens'].fillna('')

    # Filter out rows where 'Diets' contains removeDietID
    # Set na=False to treat NaN results as False
    if removeDietID_str:
        ingredientsSheet = ingredientsSheet[~ingredientsSheet['Diets'].str.contains(removeDietID_str,case = False, na=False)]
    if removeDietID_int is not None:
        ingredientsSheet = ingredientsSheet[ingredientsSheet['Diets'] != removeDietID_int]

    # Filter out rows where 'Allergens' contains removeAllergenID
    if removeAllergenID_str:
        ingredientsSheet = ingredientsSheet[~ingredientsSheet['Allergens'].str.contains(removeAllergenID_str, na=False, case= False)]
    if removeAllergenID_int is not None:
        ingredientsSheet = ingredientsSheet[ingredientsSheet['Allergens'] != removeAllergenID_int]

    # Remove records where 'Name' contains any disliked words
    if dislikes:
        dislikes_list = [ingredient.strip().lower() for ingredient in dislikes]
        ingredientsSheet = ingredientsSheet[~ingredientsSheet['Name'].apply(lambda x: any(word in x.lower().split() for word in dislikes_list))]

    return ingredientsSheet
