# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 13:53:25 2024

@author: cckk4
"""

import cProfile
import SQLConnection
import MealPlan


# Profile the generate_meal_plan function
sheets = SQLConnection.loadData()
diet = ""
allergen = ""
dislikes = ""
numberDays = 3
x = SQLConnection.generateMealPlan(sheets, diet, allergen, dislikes, numberDays)
print(x)