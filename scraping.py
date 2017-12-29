# scrape ingredients from www.vegrecipesofindia.com
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import time

def get_links(url):
   
    page = urlopen(url)
    soup = BeautifulSoup(page)
    links = []
 
    for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
        links.append(link.get('href'))
 
    return links


def get_ingredients(recipe, recipe_name):
    
    ingredient_tags = recipe.select(".wprm-recipe-ingredient")
    
    names = []
    amounts = []
    units = []
    notes = []
    
    for ingredient in ingredient_tags:
        
        try:
            name = ingredient.select(".wprm-recipe-ingredient-name")[0].get_text()
        except:
            print("No ingredient name found!")
        
        try:
            amount = [ingredient.select(".wprm-recipe-ingredient-amount")[0].get_text()
        
        except:
            amount = ""
        	
        try:
            unit = ingredient.select(".wprm-recipe-ingredient-unit")[0].get_text()
        except:
            unit = ""
        
        try:
            note = ingredient.select(".wprm-recipe-ingredient-notes")[0].get_text()
        except:
            note = ""
    
        names.append(name)
        amounts.append(amount)
        units.append(unit)
        notes.append(note)
        
    # compile into a little dataframe
    df = pd.DataFrame({
            
            'name': names,
            'amount': amounts,
            'units': units,
            'notes': notes
    })
    
    df['recipe'] = recipe_name
    
    return df