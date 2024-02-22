# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 18:24:36 2024

@author: cckk4
"""
import pandas as pd
import userFunctions  
import os
import functionFile
import openai
import cgitb 
cgitb.enable()
import importlib
importlib.reload(functionFile)
from sqlalchemy import create_engine


cgitb.enable()

os.chdir("C:/Users/cckk4/OneDrive/Documents/FYP")


def filterIngredientsSheet(ingredientsSheet, dietSheet, 
                                allergenSheet, dietary_preferences, allergies, dislike_list):
    # Remove diets and allergens from the sheet
    remove_diet_id_str = str(userFunctions.removeDietsByID(dietary_preferences, dietSheet))
    remove_diet_id_int = userFunctions.removeDietsByID(dietary_preferences, dietSheet)
    remove_allergen_id_str = str(userFunctions.removeAllergensByID(allergies, allergenSheet))
    remove_allergen_id_int = userFunctions.removeAllergensByID(allergies, allergenSheet)

    # Filter the ingredients based on user input
    filtered_sheet = userFunctions.filterIngredients(
        ingredientsSheet.copy(),
        remove_diet_id_str,
        remove_diet_id_int,
        remove_allergen_id_str,
        remove_allergen_id_int,
        dislikes=dislike_list
    )
    
    return filtered_sheet




def run(diet, allergen, dislikes, numberDays):
    
    # Database connection parameters
    db_params = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'decade10',
        'database': 'onestopfoodshop',
        'port': 3306  
    }


    db_engine = create_engine(f"mysql+mysqlconnector://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}")

    try:
        # Fetch data from the database
        allergenSheet = pd.read_sql("SELECT * FROM allergens;", db_engine)
        dietSheet = pd.read_sql("SELECT * FROM diets;", db_engine)
        ingredientsSheet = pd.read_sql("SELECT * FROM ingredients;", db_engine)
        basesSheet = pd.read_sql("SELECT * FROM bases;", db_engine)
        meal_type_classification_table = pd.read_sql("SELECT * FROM protein_base_dish;", db_engine)
        dishSheet = pd.read_sql("SELECT * FROM dishes;", db_engine)
        ingredient_grouping_table = pd.read_sql("SELECT * FROM ingredient_dish;", db_engine)

        ingredientsSheet['meals'] = ingredientsSheet.apply(lambda row: functionFile.normal_round(row['ShopQuantity'] / row['SingleServing'])
                                                            if row['ID'] > 0 else '', axis=1)
    finally:
      
        pass
        

    #print(ingredientsSheet)
    openai.api_key = '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'

    # USER INPUT 

    dietaryPreferences = diet

    # Currently only takes one allergy- need to update this
    allergies = allergen

    dislikeList = dislikes.split(',')

    daysInPlan = int(numberDays)


    filtered_sheet = filterIngredientsSheet(ingredientsSheet, dietSheet, 
                                                         allergenSheet,dietaryPreferences,
                                                         allergies, dislikeList)

    # This ensures that the same ingredient is not inlcuded in every single day of the plan 
    filtered_sheet['meals'] = pd.to_numeric(filtered_sheet['meals'], errors='coerce')

    ingredientsSheet = filtered_sheet[filtered_sheet['meals'] <= daysInPlan]
    
    pd.set_option('display.max_columns', None)
    # Get protein sample
    proteinIndices = functionFile.chooseProteins(ingredientsSheet, daysInPlan)
   # print(filtered_sheet)
    # Get the number of meals each protein must be used in to be completely used up
    proteinNumberMeals = functionFile.getNumberMeals(proteinIndices, daysInPlan, ingredientsSheet)

    # Put the protein indices and number of meals in a seperate dataframe
    proteinMealsDataframe = functionFile.getIngredientMealsDataframe(ingredientsSheet, proteinIndices)

    # Create a list where the protein index appears an amount of times = to its numer of meals
    proteinListByNumberMeals = functionFile.duplicatedList(proteinMealsDataframe, proteinNumberMeals)

    # Assign a suitable base index to the protein and use the protein-base pair to assign a dish type
    dishIndices, baseIndices = functionFile.getDishIndices(proteinListByNumberMeals, meal_type_classification_table) 

    # Compile dish, base and protein IDs into one dataframe
    dishBaseProteinDataframe = functionFile.createDishBaseProteinDataframe(dishIndices, baseIndices, proteinListByNumberMeals)

    # Score the vegetables based on the number of dishes they could be used in
    vegScoreDataframe = functionFile.calculate_veg_score(dishBaseProteinDataframe, ingredient_grouping_table)
   
    # Get the top scoring vegetables and use these as the vegetables in the meal plan
    vegetableIndices = functionFile.top_scorers(vegScoreDataframe, daysInPlan)
  
    # Get the number of meals each veg must be used in 
    vegNumberMeals = functionFile.getNumberMeals(vegetableIndices, daysInPlan, ingredientsSheet)

    # Combine veg and meals in a dataframe
    vegetableMealsDataframe = functionFile.getIngredientMealsDataframe(ingredientsSheet, vegetableIndices)

    # Create a list where the veg index appears an amount of times = to its numer of meals
    vegetableListByNumberMeals = functionFile.duplicatedList(vegetableMealsDataframe, vegNumberMeals)

    vegetablesByDay = functionFile.divide_strings(vegetableListByNumberMeals, daysInPlan)

    # Combine the above set of arrays with the protein, base and dish IDs
    result_df = functionFile.vegBaseProteinDish(vegetablesByDay, dishBaseProteinDataframe)

    # Remove null entries 
    result_df = functionFile.completeDataframe(result_df)

    # Replace index entries with corresponding string names
    df_check = functionFile.replaceIndicesWithStrings(result_df, ingredientsSheet, basesSheet, dishSheet)

    
    # Generate a list of recipes
    recipes = []

    for _, row in df_check.iterrows():
        recipe = functionFile.generateRecipe(openai.api_key, row, dietaryPreferences, allergies)
        recipes.append(recipe)

    return recipes

