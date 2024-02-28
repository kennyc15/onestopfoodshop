# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 18:24:36 2024

@author: cckk4
"""
import pandas as pd
import IngredientFilter  
import os
import MealPlan
import openai
import cgitb 
cgitb.enable()
import importlib
importlib.reload(MealPlan)
from sqlalchemy import create_engine

cgitb.enable()

os.chdir("C:/Users/cckk4/OneDrive/Documents/FYP")

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

        ingredientsSheet['meals'] = ingredientsSheet.apply(lambda row: MealPlan.normal_round(row['ShopQuantity'] / row['SingleServing'])
                                                            if row['ID'] > 0 else '', axis=1)
    finally:
      
        pass
        
    openai.api_key = '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'

    # USER INPUT 

    dietaryPreferences = diet

    allergies = allergen

    dislikeList = dislikes.split(',')

    daysInPlan = int(numberDays)


    filtered_sheet = IngredientFilter.filterIngredientsSheet(ingredientsSheet, dietSheet, 
                                                         allergenSheet,dietaryPreferences,
                                                         allergies, dislikeList)

    # This ensures that the same ingredient is not inlcuded in every single day of the plan 
    filtered_sheet['meals'] = pd.to_numeric(filtered_sheet['meals'], errors='coerce')

    ingredientsSheet = filtered_sheet[filtered_sheet['meals'] <= daysInPlan]
    
    # Get protein sample
    proteinIndices = MealPlan.chooseProteins(ingredientsSheet, daysInPlan)

    # Get the number of meals each protein must be used in to be completely used up
    proteinNumberMeals = MealPlan.getNumberMeals(proteinIndices, daysInPlan, ingredientsSheet)

    # Put the protein indices and number of meals in a seperate dataframe
    proteinMealsDataframe = MealPlan.getIngredientMealsDataframe(ingredientsSheet, proteinIndices)

    # Create a list where the protein index appears an amount of times = to its numer of meals
    proteinListByNumberMeals = MealPlan.duplicatedList(proteinMealsDataframe, proteinNumberMeals)

    # Assign a suitable base index to the protein and use the protein-base pair to assign a dish type
    dishIndices, baseIndices = MealPlan.getDishIndices(proteinListByNumberMeals, meal_type_classification_table) 

    # Compile dish, base and protein IDs into one dataframe
    dishBaseProteinDataframe = MealPlan.createDishBaseProteinDataframe(dishIndices, baseIndices, proteinListByNumberMeals)

    # Score the vegetables based on the number of dishes they could be used in
    vegScoreDataframe = MealPlan.calculateVegScore(dishBaseProteinDataframe, ingredient_grouping_table)
   
    # Get the top scoring vegetables and use these as the vegetables in the meal plan
    vegetableIndices = MealPlan.getTopScorers(vegScoreDataframe, daysInPlan)
  
    # Get the number of meals each veg must be used in 
    vegNumberMeals = MealPlan.getNumberMeals(vegetableIndices, daysInPlan, ingredientsSheet)

    # Combine veg and meals in a dataframe
    vegetableMealsDataframe = MealPlan.getIngredientMealsDataframe(ingredientsSheet, vegetableIndices)

    # Create a list where the veg index appears an amount of times = to its numer of meals
    vegetableListByNumberMeals = MealPlan.duplicatedList(vegetableMealsDataframe, vegNumberMeals)

    vegetablesByDay = MealPlan.divideStrings(vegetableListByNumberMeals, daysInPlan)

    # Combine the above set of arrays with the protein, base and dish IDs
    result_df = MealPlan.vegBaseProteinDish(vegetablesByDay, dishBaseProteinDataframe)

    # Remove null entries 
    result_df = MealPlan.completeDataframe(result_df)

    # Replace index entries with corresponding string names
    df_check = MealPlan.replaceIndicesWithStrings(result_df, ingredientsSheet, basesSheet, dishSheet)

    
    # Generate a list of recipes
    recipes = []

    for _, row in df_check.iterrows():
        recipe = MealPlan.generateRecipe(openai.api_key, row, dietaryPreferences, allergies)
        recipes.append(recipe)

    return recipes

