# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 20:00:04 2024

@author: cckk4
"""


def removeAllergensByID(allergies, allergenSheet):
    """Removes the ingredients that contain user allergens."""
    allergies = [allergies]
    allergenSheet['Name'] = allergenSheet['Name'].str.strip()

    # Proceed with filtering
    filtered_df = allergenSheet[allergenSheet['Name'].isin(allergies)]

    # Check if the filtered DataFrame is not empty and retrieve the value
    if not filtered_df.empty:
        retrieved_value = filtered_df['ID'].iloc[0]
        return int(retrieved_value)
    else:
        return "No matching row found"
    
def removeDietsByID(dietaryPreferences, dietSheet):
    """Removes ingredients unsuitable for given dietary preferences."""
    dietaryPreferences = [dietaryPreferences]
    dietSheet['Name'] = dietSheet['Name'].str.strip()

    # Proceed with filtering
    filtered_df = dietSheet[dietSheet['Name'].isin(dietaryPreferences)]

    # Check if the filtered DataFrame is not empty and retrieve the value
    if not filtered_df.empty:
        retrieved_value = filtered_df['ID'].iloc[0]
        return int(retrieved_value)
    else:
        return "No matching row found"
        

def filterIngredients(ingredientsSheet, removeDietID_str='', removeDietID_int=None,
                      removeAllergenID_str='', removeAllergenID_int=None, dislikes=None):
    """Filters ingredients from the main ingredients sheet before creating a meal plan."""
    # Replace NaN with an empty string before applying str.contains()
    ingredientsSheet['Diets'] = ingredientsSheet['Diets'].fillna('')
    ingredientsSheet['Allergens'] = ingredientsSheet['Allergens'].fillna('')

    # Filter out rows based on 'Diets' and 'Allergens'
    if removeDietID_str:
        ingredientsSheet = ingredientsSheet[~ingredientsSheet['Diets'].str.contains(removeDietID_str, case=False, na=False)]
    if removeDietID_int is not None:
        ingredientsSheet = ingredientsSheet[ingredientsSheet['Diets'] != removeDietID_int]
    if removeAllergenID_str:
        ingredientsSheet = ingredientsSheet[~ingredientsSheet['Allergens'].str.contains(removeAllergenID_str, na=False, case=False)]
    if removeAllergenID_int is not None:
        ingredientsSheet = ingredientsSheet[ingredientsSheet['Allergens'] != removeAllergenID_int]

    # Remove records where 'Name' contains any disliked words
    if dislikes:
        dislikes_list = [ingredient.strip().lower() for ingredient in dislikes]
        ingredientsSheet = ingredientsSheet[~ingredientsSheet['Name'].apply(lambda x: any(word in x.lower().split() for word in dislikes_list))]

    return ingredientsSheet

def filterIngredientsSheet(ingredientsSheet, dietSheet, allergenSheet, dietary_preferences, allergies, dislike_list):
    """Integrates all filters and returns a filtered ingredients sheet."""
    # Remove diets and allergens from the sheet
    remove_diet_id_str = str(removeDietsByID(dietary_preferences, dietSheet))
    remove_allergen_id_str = str(removeAllergensByID(allergies, allergenSheet))

    # Filter the ingredients based on user input
    filtered_sheet = filterIngredients(
        ingredientsSheet.copy(),
        removeDietID_str=remove_diet_id_str,
        removeDietID_int=removeDietsByID(dietary_preferences, dietSheet),
        removeAllergenID_str=remove_allergen_id_str,
        removeAllergenID_int=removeAllergensByID(allergies, allergenSheet),
        dislikes=dislike_list
    )
    
    return filtered_sheet