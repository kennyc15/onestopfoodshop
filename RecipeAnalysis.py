# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 23:28:07 2024

@author: cckk4
"""
import json
import os
import pandas as pd
import SQLConnection  # Assuming this is a module you have that connects to a database

os.chdir("C:/Users/cckk4/OneDrive/Documents/FYP")

# Load your CSV file into a pandas DataFrame
df = pd.read_csv('recipes.csv')

# Load extended base ingredients from JSON files
def load_extended_bases(*json_files):
    extended_bases = {}
    for json_file in json_files:
        base_name = os.path.splitext(os.path.basename(json_file))[0]  # Extract base name from file name
        with open(json_file, 'r') as file:
            extended_bases[base_name] = set(json.load(file))
    return extended_bases

# Function to count the occurrences of base-protein pairs in the RecipeIngredients column
def count_base_protein_pairs_in_csv(df, base_list, protein_list, extended_bases):
    pair_counts = {(base, protein): 0 for base in base_list for protein in protein_list}

    # Function to clean and extract ingredients from the column format
    def clean_and_extract(ingredients_str):
        # Trim the leading 'c(' and trailing ')' and split by '", "'
        cleaned_str = ingredients_str.strip('c()').replace('"', '')
        ingredients = cleaned_str.split(', ')
        return set(ingredient.lower() for ingredient in ingredients)

    for index, row in df.iterrows():  # Iterate through each row in the DataFrame
    # Check if the entry is a string
        if isinstance(row['RecipeIngredientParts'], str):
            ingredients_set = clean_and_extract(row['RecipeIngredientParts'].lower())
        else:
            # Handle the case where the entry is not a string
            # You could convert to string or decide to continue, depending on your needs
            ingredients_set = clean_and_extract(str(row['RecipeIngredientParts']).lower())
    
        ingredients_text = " ".join(ingredients_set)  # Join all ingredients into a single string

    
        for base in base_list:
            base_key = base.lower().replace(" ", "")
            # Assuming matched_bases is being retrieved from extended_bases
            matched_bases = {base_part.lower() for base_part in extended_bases.get(base_key, {base.lower()})}
            base_match = any(base_part in ingredients_text for base_part in matched_bases)
    
            if base_match:  # If a base match is found, then look for a protein match
                for protein in protein_list:
                    protein_key = protein.lower()
                    protein_match = protein_key in ingredients_text  # Check if the protein is in the ingredients text
    
                    if protein_match:  # Only need to check protein_match here
                        pair_counts[(base, protein)] += 1



    return pair_counts

# Load the extended bases
extended_bases = load_extended_bases('bread.json', 'saladgrain.json', 'pasta.json', 'rice.json', 'noodles.json')
tables = SQLConnection.loadData()
proteins = tables['ingredientsSheet']['Name'].tolist()

def create_normalized_df(df, extended_bases, bases_sheet, ingredients_sheet):
    """
    Create a normalized DataFrame with replaced column and index headings with base and protein IDs.
    
    Parameters:
    - df: DataFrame containing the recipe data.
    - extended_bases: List of extended bases.
    - bases_sheet: DataFrame containing base information.
    - ingredients_sheet: DataFrame containing ingredient information.
    
    Returns:
    - DataFrame: Normalized DataFrame with replaced headings.
    """
    tables = SQLConnection.loadData()
    bases = tables['basesSheet']['Name']
    proteins_df = tables['ingredientsSheet'][tables['ingredientsSheet']['Macro'] == 'P']
    proteins = proteins_df['Name'].tolist()
    bases_df = tables['basesSheet']
    proteins_df = tables['ingredientsSheet'][tables['ingredientsSheet']['Macro'] == 'P']


    # Count the base-protein pairs
    pair_counts = count_base_protein_pairs_in_csv(df, bases, proteins, extended_bases)

    # Create DataFrame with base and protein IDs
    matrix_df = pd.DataFrame(index=proteins, columns=bases, data=0)  # Fill with zeros

    # Update the DataFrame with counts
    for (base, protein), count in pair_counts.items():
        if count > 0:  # Only consider pairs that occur at least once
            matrix_df.at[protein, base] = count

    normalized_df = matrix_df.div(matrix_df.sum(axis=1), axis=0)
    
    # Replace column and index headings with base and protein IDs
    normalized_df.columns = bases_df['ID']
    normalized_df.index = proteins_df['ID']

    return normalized_df

# In one file (let's call it script1.py)
normalized_df = create_normalized_df(df, extended_bases, tables['basesSheet'], tables['ingredientsSheet'])

# Save the normalized DataFrame to a file
normalized_df.to_csv('normalized_data.csv', index=True)  # Adjust the filename and path as needed



def calculate_protein_fractions(df, protein_list):
    """
    Calculate the fraction of times each protein appears in the 
    RecipeIngredientParts column relative to all protein matches.
    
    Parameters:
    - df: DataFrame containing the recipe data.
    - protein_list: List of all proteins to search for in the recipes.
    
    Returns:
    - Dictionary with proteins as keys and their appearance fraction as values.
    """
    # Initialize counters
    protein_counts = {protein.lower(): 0 for protein in protein_list}
    total_protein_matches = 0
    
    # Iterate over each row in the DataFrame
    for ingredients_str in df['RecipeIngredientParts'].str.lower():
        for protein in protein_list:
            protein_lower = protein.lower()
            if protein_lower in ingredients_str:
                protein_counts[protein_lower] += 1
                total_protein_matches += 1
    
    # Calculate fractions
    protein_fractions = {protein: count / total_protein_matches if total_protein_matches > 0 else 0 
                         for protein, count in protein_counts.items()}
    
    return protein_fractions

proteins_df = tables['ingredientsSheet'][tables['ingredientsSheet']['Macro'] == 'P']
proteins_df = proteins_df[proteins_df['Macro'] == 'P']['Name']
print(calculate_protein_fractions(df, proteins_df))
