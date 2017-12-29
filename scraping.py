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
            amount = [ingredient.select(".wprm-recipe-ingredient-amount")[0].get_text()]
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

def get_recipe_details(soup):
    
    #url
    url = soup.find("meta",  property="og:url")["content"]


    # name
    title = soup.find("meta",  property="og:title")["content"]

    name = title.partition('recipe')[0]

    # description
    description = title.partition('recipe')[2]

    # tags
    tag_tags = soup.find_all("meta", property="article:tag")
    tags = []
    for tag in tag_tags:
        tags.append(tag['content'])

    # sections
    section_tags = soup.find_all("meta", property="article:section")
    sections = []
    for section in section_tags:
        sections.append(section['content'])

    #categories
    categories = soup.find(class_='entry-categories').get_text()[13:].split(",")

    all_labels = tags + sections + categories
    labels = ",".join(list(set(all_labels)))
    

    # has photos
    has_photos = False
    if "step by step photos" in soup.find("meta", property="og:description")["content"]:
        has_photos = True

    ings = soup.find(class_ ="wprm-recipe-container")


    # prep time
    prep_time = [ings.get_text().partition('"prepTime":"')[2].partition('",')[0][2:-1]]

    # cook time
    cook_time = [ings.get_text().partition('"cookTime":"')[2].partition('",')[0][2:-1]]

    # total time
    total_time = [ings.get_text().partition('"totalTime":"')[2].partition('",')[0][2:-1]]

    # calories per serving
    calories = [ings.get_text().partition('"calories":"')[2].partition(' kcal')[0]]


    # course
    try:
        course = re.sub('\s+', '', soup.find(class_ ="wprm-recipe-course-container").get_text()).partition(":")[2]
    except:
        course = ''
        
    # cuisine
    try:
        cuisine = re.sub('\s+', '', soup.find(class_ ="wprm-recipe-cuisine-container").get_text()).partition(":")[2]
    except:
        cuisine = ''
        
    # no of servings
    try:
        servings = re.sub('\s+', '', soup.find(class_ ="wprm-recipe-servings-container").get_text()).partition(":")[2]
    except:
        servings = ''
    # if there is something like 3 to 4, take the average - do this later

    # total fat
    try:
        total_fat = [ings.get_text().partition('"fatContent":"')[2].partition(' g')[0]]
    except:
        total_fat = ''
        
    # saturated fat
    try:
        saturated_fat = [ings.get_text().partition('"saturatedFatContent":"')[2].partition(' g')[0]]
    except:
        saturated_fat = ''
        
    # fiber
    fiber = [ings.get_text().partition('"fiberContent":"')[2].partition(' g')[0]]

    # protein
    protein = [ings.get_text().partition('"proteinContent":"')[2].partition(' g')[0]]

    # sugar
    sugar = [ings.get_text().partition('"sugarContent":"')[2].partition(' g')[0]]

    # carbs
    carbs = [ings.get_text().partition('"carbohydrateContent":"')[2].partition(' g')[0]]

    # rating
    rating = [ings.get_text().partition('"ratingValue":"')[2].partition('",')[0]]
    
    # combine into df
    df = pd.DataFrame({
            
            'name': name,
            'description': description,
            'labels': labels,
            'photos': has_photos,
            'prep_time': prep_time,
            'cook_time': cook_time,
            'total_time': total_time,
            'calories': calories,
            'course': course,
            'cuisine': cuisine,
            'servings': servings,
            'total_fat': total_fat,
            'saturated_fat' : saturated_fat,
            'protein': protein,
            'sugar': sugar,
            'carbs': carbs,
            'rating': str(rating),
            'url': url
        })
    return name, df

def do_stuff(url):
    print(url)
    if "comment" in url:
        print("No recipe found")
        return
    if ".com/hi" in url:
        print("Hindi. Ignoring")
        return

    try:
    	page = requests.get(url)
    
    except:
    	print("Sleeping for 30 seconds")
    	time.sleep(30)

    if not page.status_code == 200:
        print("Page not found")
        return
    
    soup = BeautifulSoup(page.content, 'html.parser')
    recipe = soup.find(class_ ="wprm-recipe-ingredients-container")
    if recipe is None:
        print("No recipe found on this page")
        return
    print("Recipe Found")
    name, recipe_details = get_recipe_details(soup)
    ingredients = get_ingredients(recipe,name)
    return recipe_details, ingredients


master_url = "http://www.vegrecipesofindia.com/recipes-index/"
main_links = get_links(master_url)
master_links = []
for link in main_links:
    master_links += get_links(link)
links = list(set(master_links))

recipes = pd.DataFrame({            
            'name': [],
            'description': [],
            'labels': [],
            'photos': [],
            'prep_time': [],
            'cook_time': [],
            'total_time': [],
            'calories': [],
            'course': [],
            'cuisine': [],
            'servings': [],
            'total_fat': [],
            'saturated_fat' : [],
            'protein': [],
            'sugar': [],
            'carbs': [],
            'rating': []
        })

ingredients =  pd.DataFrame({
            
            'name': [],
            'amount': [],
            'units': [],
            'notes': [],
            'recipe': []
    })

 for k in range(len(links)):
    print(k)
        
    do_stuff(links[k])
    if r is not None and i is not None:
        recipes.append(r)
        ingredients.append(i)

