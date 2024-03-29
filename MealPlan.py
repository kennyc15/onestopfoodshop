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

def chooseProteins(ingredientsSheet, days):
    """Picks the Protein Sample considering the number of days in the plan."""
    numProteins = math.floor(days / 2)

    while True:
        proteins = ingredientsSheet[ingredientsSheet['Macro'] == 'P']
        proteins = proteins[proteins['meals'] <= days]
        
        if proteins.empty:
            return None

        probs = proteins['Frequency'] / proteins['Frequency'].sum()
        validMask = proteins['meals'] <= days
        validProbs = np.where(validMask, probs, 0)
        validProbs /= validProbs.sum()

        proteinSample = np.random.choice(proteins['ID'], size=numProteins, replace=False, p=validProbs)

        if proteins.loc[proteins['ID'].isin(proteinSample), 'meals'].sum() == days:
            return proteinSample

def getDishIndices(proteinIndicesList, proteinDishDataframe):
    """Chooses a base and gets the corresponding Dish ID for the protein and base."""
    usedBaseIds = {protein_id: set() for protein_id in proteinIndicesList}
    dishIDsList, baseIDsList = [], []

    for proteinToLookup in proteinIndicesList:
        boolValue = True

        while boolValue:
            available_base_ids = set(range(1, 7)) - usedBaseIds[proteinToLookup]
            if not available_base_ids:
                usedBaseIds[proteinToLookup] = set()

            base_id_to_lookup = random.choice(list(available_base_ids))
            result = proteinDishDataframe.loc[
                (proteinDishDataframe['Protein_ID'] == proteinToLookup) &
                (proteinDishDataframe['Base_ID'] == base_id_to_lookup), 'Dish_ID']

            if not result.empty:
                dishID = result.iloc[0]
                dishIDsList.append(dishID)
                baseIDsList.append(base_id_to_lookup)
                usedBaseIds[proteinToLookup].add(base_id_to_lookup)
                boolValue = False
            else:
                boolValue = True

    return dishIDsList, baseIDsList

def getNumberMeals(indices, daysInPlan, ingredientsSheet):
    """Gets the number of meals that will have a protein."""
    totalNumMeals = np.sum(ingredientsSheet.loc[ingredientsSheet['ID'].isin(indices), 'meals'])
    return totalNumMeals

def duplicatedList(ingMealCounter, totalPortions):
    """Lists the proteins based on how many meals they are included in."""
    v, boolVal = [], False

    while not boolVal:
        id_list = ingMealCounter['ID'].tolist()
        x = random.choice(id_list)
        matching = ingMealCounter.index[ingMealCounter['ID'] == x]
        
        if len(matching) > 0:
            index_x = matching[0]
            if ingMealCounter.at[index_x, 'meals'] != 0:
                v.append(x)
                ingMealCounter.at[index_x, 'meals'] -= 1
                ingMealCounter = ingMealCounter[ingMealCounter['meals'] > 0]
                
                if len(v) == totalPortions:
                    boolVal = True

    return v

def getIngredientMealsDataframe(ingredientSheet, ingredientIndices):
    """Returns a dataframe with protein indices and corresponding number of meals."""
    ingCounter = ingredientSheet[ingredientSheet['ID'].isin(ingredientIndices)][['ID', 'meals']]
    return ingCounter

def createDishBaseProteinDataframe(dish, base, protein):
    """Combines dish, base, and protein selections in one dataframe."""
    return pd.DataFrame({'Dish_ID': dish, 'Base_ID': base, 'Protein_ID': protein})


def calculateVegScore(df1, df2):
    """Scores vegetables based on how many of the dishes they can go into."""
    resultDF = pd.DataFrame(columns=['ingredientID', 'Score'])

    for dishID in df1['Dish_ID']:
        matches = df2.loc[df2['DishID'] == dishID, 'IngredientID']

        for ingredientID in matches:
            if not resultDF.empty and ingredientID in resultDF['ingredientID'].values:
                resultDF.loc[resultDF['ingredientID'] == ingredientID, 'Score'] += 1
            else:
                resultDF = pd.concat([resultDF, pd.DataFrame({'ingredientID': [ingredientID], 'Score': [1]})], ignore_index=True)

    return resultDF

def getTopScorers(vegScoreDataframe, size):
    """Returns the IDs of vegetables based on the specified size."""
    size = random.choice([size+1, size+2])
    sortedDF = vegScoreDataframe.sort_values(by='Score', ascending=False)
    return sortedDF.head(size)['ingredientID'].tolist()


def divideStrings(input_vector, x):
    """Gives the vegetable combinations for recipes each day, ensuring unique combinations."""
    if len(np.unique(input_vector)) < x:
        raise ValueError("Not enough unique elements in the input vector for division.")
    
    boolVal = False
    while not boolVal:
        shuffled_vector = random.sample(input_vector, len(input_vector))
        substrings = np.array_split(shuffled_vector, x)
        maxLength = max(len(substring) for substring in substrings)
        substrings = [np.pad(substring, (0, maxLength - len(substring)), 'constant') for substring in substrings]
        boolVal = all(len(np.unique(substring)) == len(substring) for substring in substrings)
            
    return substrings

def generateVegCombinations(vegScoreDataframe, daysInPlan, divisionCount):
    numVegLow = daysInPlan + 2  # Initial lower bound for vegetable count
    retry = True
    
    while retry:
        try:
            # Attempt to divide strings with current size
            size = numVegLow  # Start with the initial or updated size
            vegIDs = getTopScorers(vegScoreDataframe, size)
            divideStrings(vegIDs, divisionCount)
            retry = False  # If divideStrings succeeds, exit loop
        except ValueError:
            # If not enough unique elements, increase the size and retry
            numVegLow += 1  # Increment size for next attempt

    return vegIDs


def vegBaseProteinDish(vegetablesByDay, DishBaseProteinDataframe):
    """Combines veg, protein, base, and dish id for a given day."""
    maxLength = max(len(arr) for arr in vegetablesByDay)
    column_names = [f'Veg{i+1}' for i in range(maxLength)]
    vegDf = pd.DataFrame(vegetablesByDay, columns=column_names)
    resultDF = pd.concat([vegDf, pd.DataFrame(DishBaseProteinDataframe)], axis=1)
    result_columns = [col for col in resultDF.columns if col not in ['Dish_ID', 'Base_ID', 'Protein_ID']] + ['Dish_ID', 'Base_ID', 'Protein_ID']
    return resultDF[result_columns]

def completeDataframe(data):
    """Ensures the dataframe has no NaN entries and assigns dish ID based on rules."""
    df = pd.DataFrame(data).fillna(0)
    mask = (df['Dish_ID'] == 0) & (df['Base_ID'] == 0)
    random_numbers = np.random.randint(1, 7, size=sum(mask))
    df.loc[mask, 'Base_ID'] = random_numbers
    rules = {1: 12, 2: 1, 3: 2, 4: 6, 5: 3, 6: 4}
    df.loc[mask, 'Dish_ID'] = df.loc[mask, 'Base_ID'].map(rules)
    df[['Dish_ID', 'Base_ID', 'Protein_ID']] = df[['Dish_ID', 'Base_ID', 'Protein_ID']].astype(int)
    return df


# Parameters: completed dataframe, ingredients sheet, base sheet, dish sheet
    
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
    
    for col in columns_replace_A:
        df_check[col] = df_check[col].apply(lambda x: df_A.loc[df_A['ID'] == int(x), 'Name'].values[0] if (isinstance(x, (int, float)) and x != 0 and int(x) in df_A['ID'].values) else x)
    for col in columns_replace_B:
        df_check[col] = df_check[col].apply(lambda x: df_B.loc[df_B['ID'] == int(x), 'Name'].values[0] if (isinstance(x, (int, float)) and x != 0 and int(x) in df_B['ID'].values) else x)   
    for col in columns_replace_C:
        df_check[col] = df_check[col].map(lambda x: df_C.loc[df_C['ID'] == int(x), 'Name'].values[0] if (isinstance(x, (int, float)) and x != 0 and int(x) in df_C['ID'].values) else x)
    df_check = df_check.map(lambda x: df_D.loc[df_D['ID'] == int(x), 'Name'].values[0] if (isinstance(x, (int, float)) and x != 0 and int(x) in df_D['ID'].values) else x)
    
    return df_check


def getServings(proteinIDs, vegIDs, data):
    """
    Calculates the servings of fresh ingredients for each recipe as a fraction of meals.
    """
    merge = proteinIDs + vegIDs
    df = pd.DataFrame(data)
    df['Fractions'] = df['meals'].apply(lambda x: Fraction(1, int(x)))
    filtered_df = df[df['ID'].isin(merge)]
    return filtered_df[['Name', 'Fractions']]

def replaceNewlines(text):
    """
    Replaces variations of newline characters with actual line breaks.
    """
    return text.replace("\\n", "\n").replace("\n", "\n")

def convertRecipesToDict(recipesList):
    """
    Converts a list of recipe strings to a dictionary with recipe titles as keys.
    """
    formatted_str = "[" + ",".join(recipesList) + "]"
    try:
        recipesList = json.loads(formatted_str)
        recipesDict = {recipe["recipe_title"]: recipe for recipe in recipesList}
        return recipesDict
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def convertListToRecipeDict(recipe_list):
    """
    Parses each string in a list as JSON and adds it to a dictionary with the title as the key.
    """
    recipesDict = {}
    for recipe_str in recipe_list:
        recipe = json.loads(recipe_str)
        recipesDict[recipe["recipe_title"]] = recipe
    return recipesDict

def generateRecipe(api_key, row, diet, allergen):
    """
    Generates a recipe using OpenAI's API based on the provided ingredients and dietary requirements.
    """
    openai.api_key = api_key
    vegetables = [row[f'Veg{i}'] for i in range(1, len(row) - 3 + 1)]
    protein = row['Protein_ID']
    base = row['Base_ID']
    dishID = row['Dish_ID']
    
    # Construct prompt 
    prompt = f"""Create a recipe with {', '.join(map(str, vegetables))} as vegetables,
        {protein} as protein, and {base} as the base.
        If there are allergens or dietary requirements, they are; {diet, allergen}
        Do not use any other fresh vegetables or proteins.
        You may use pantry items such as spices, sauces, and others that do not expire.
        Give the recipe a creative, fun name relevant for a {dishID} dish.
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
                "Preheat oven to 180 degrees celcius."
                "Cook the pasta according to package instructions, then drain and set aside.",
                "In a large pan, heat olive oil over medium heat. Add minced garlic and red pepper flakes, and cook until fragrant.",
                "Add sliced red onion and cook until translucent. Then add the cherry tomatoes and sundried tomatoes, cook for a few minutes until softened.",
                "Add the kidney beans and cooked pasta to the pan. Season with salt and black pepper, then toss everything together until well combined.",
                "Turn off the heat and stir in the arugula until it wilts slightly.",
                "Serve the Tomato Tango Pasta hot, garnished with some extra arugula leaves."
            ],
            "notes": "Feel free to top with some grated Parmesan cheese or a drizzle of balsamic glaze for extra flavour."
          }}
          """



    # Call API 
    response = openai.ChatCompletion.create(
           model="gpt-3.5-turbo", temperature=0.7,
           messages=[
               {"role": "system", "content": "You are a recipe creator."},
               {"role": "user", "content": prompt},
           ],
           max_tokens=1200,
       )
    return replaceNewlines(response['choices'][0]['message']['content'])