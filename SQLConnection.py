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

def loadData():
    # Database connection parameters
    db_params = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'decade10',
        'database': 'onestopfoodshop',
        'port': 3306  
    }

    # Create database engine
    db_engine = create_engine(f"mysql+mysqlconnector://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}")

    sheets = {}
    try:
        # Fetch data from the database
        sheets['allergenSheet'] = pd.read_sql("SELECT * FROM allergens;", db_engine)
        sheets['dietSheet'] = pd.read_sql("SELECT * FROM diets;", db_engine)
        sheets['ingredientsSheet'] = pd.read_sql("SELECT * FROM ingredients;", db_engine)
        sheets['basesSheet'] = pd.read_sql("SELECT * FROM bases;", db_engine)
        sheets['mealTypeClassificationTable'] = pd.read_sql("SELECT * FROM protein_base_dish;", db_engine)
        sheets['dishSheet'] = pd.read_sql("SELECT * FROM dishes;", db_engine)
        sheets['ingredientGroupingTable'] = pd.read_sql("SELECT * FROM ingredient_dish;", db_engine)

        sheets['ingredientsSheet']['meals'] = sheets['ingredientsSheet'].apply(
            lambda row: MealPlan.normal_round(row['ShopQuantity'] / row['SingleServing'])
            if row['ID'] > 0 else '', axis=1)
    finally:
        db_engine.dispose()  # Ensure the connection is closed

    return sheets



def generateMealPlan(sheets, diet, allergen, dislikes, numberDays):
    # Extract sheets
    allergenSheet = sheets['allergenSheet']
    dietSheet = sheets['dietSheet']
    ingredientsSheet = sheets['ingredientsSheet']
    basesSheet = sheets['basesSheet']
    mealTypeClassificationTable = sheets['mealTypeClassificationTable']
    dishSheet = sheets['dishSheet']
    ingredientGroupingTable = sheets['ingredientGroupingTable']

    # USER INPUT PROCESSING
    dietaryPreferences = diet
    allergies = allergen
    dislikeList = dislikes.split(',')
    daysInPlan = int(numberDays)
    
    # Load the normalized DataFrame from the saved file
 #   normalized_df = pd.read_csv('normalized_data.csv', index_col=0)  # Adjust the filename and path as 
        
    openai.api_key = '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'

    filteredSheet = IngredientFilter.filterIngredientsSheet(ingredientsSheet, dietSheet, 
                                                         allergenSheet,dietaryPreferences,
                                                         allergies, dislikeList)

    # This ensures that the same ingredient is not inlcuded in every single day of the plan 
    filteredSheet['meals'] = pd.to_numeric(filteredSheet['meals'], errors='coerce')

    ingredientsSheet = filteredSheet[filteredSheet['meals'] <= daysInPlan]
    ingredientGroupingTable = ingredientGroupingTable[ ingredientGroupingTable['IngredientID'].isin(ingredientsSheet['ID'])]
    
   # Get protein sample
    proteinIndices = MealPlan.chooseProteins(ingredientsSheet, daysInPlan)

    # Get the number of meals each protein must be used in to be completely used up
    proteinNumberMeals = MealPlan.getNumberMeals(proteinIndices, daysInPlan, ingredientsSheet)

    # Put the protein indices and number of meals in a seperate dataframe
    proteinMealsDataframe = MealPlan.getIngredientMealsDataframe(ingredientsSheet, proteinIndices)

    # Create a list where the protein index appears an amount of times = to its numer of meals
    proteinListByNumberMeals = MealPlan.duplicatedList(proteinMealsDataframe, proteinNumberMeals)

    # Assign a suitable base index to the protein and use the protein-base pair to assign a dish type
    dishIndices, baseIndices = MealPlan.getDishIndices(proteinListByNumberMeals, mealTypeClassificationTable) 

    # Compile dish, base and protein IDs into one dataframe
    dishBaseProteinDataframe = MealPlan.createDishBaseProteinDataframe(dishIndices, baseIndices, proteinListByNumberMeals)

    # Score the vegetables based on the number of dishes they could be used in
    vegScoreDataframe = MealPlan.calculateVegScore(dishBaseProteinDataframe, ingredientGroupingTable)

    # Initial call replaced with a wrapper function that includes retry logic for selecting vegetables
    # vegetableIndices = MealPlan.getTopScorers(vegScoreDataframe, daysInPlan)
    vegetableIndices = MealPlan.generateVegCombinations(vegScoreDataframe, daysInPlan, divisionCount=daysInPlan)  # Adjust divisionCount as necessary
    
    # The rest of the process remains largely the same
    # Get the number of meals each veg must be used in 
    vegNumberMeals = MealPlan.getNumberMeals(vegetableIndices, daysInPlan, ingredientsSheet)
    
    # Combine veg and meals in a dataframe
    vegetableMealsDataframe = MealPlan.getIngredientMealsDataframe(ingredientsSheet, vegetableIndices)
    
    # Create a list where the veg index appears an amount of times = to its number of meals
    vegetableListByNumberMeals = MealPlan.duplicatedList(vegetableMealsDataframe, vegNumberMeals)
    
    # Directly use vegetableListByNumberMeals since generateVegCombinations ensures correctness
    vegetablesByDay = MealPlan.divideStrings(vegetableListByNumberMeals, daysInPlan)
    
    # Combine the above set of arrays with the protein, base, and dish IDs
    resultDF = MealPlan.vegBaseProteinDish(vegetablesByDay, dishBaseProteinDataframe)

    # Remove null entries 
    resultDF = MealPlan.completeDataframe(resultDF)

    # Replace index entries with corresponding string names
    dfCheck = MealPlan.replaceIndicesWithStrings(resultDF, ingredientsSheet, basesSheet, dishSheet)

    
    # Generate a list of recipes
    recipes = []

    for _, row in dfCheck.iterrows():
        recipe = MealPlan.generateRecipe(openai.api_key, row, dietaryPreferences, allergies)
        recipes.append(recipe)

    return recipes
