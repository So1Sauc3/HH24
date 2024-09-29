# Import Module 
from bs4 import BeautifulSoup 
import requests 
from fractions import Fraction
import re

def convert_fractions_to_decimal(input_string):
    # Map for Unicode fractions
    unicode_fractions = {
        '¼': Fraction(1, 4),
        '½': Fraction(1, 2),
        '¾': Fraction(3, 4),
        '⅛': Fraction(1, 8),
        '⅜': Fraction(3, 8),
        '⅝': Fraction(5, 8),
        '⅞': Fraction(7, 8),
    }

    # Replace Unicode fractions with their decimal equivalents
    for unicode_frac, fraction in unicode_fractions.items():
        input_string = input_string.replace(unicode_frac, str(float(fraction)))

    # Regex pattern for unknown fractions at the start of the string (e.g., "1/2", "3/4")
    unknown_fraction_pattern = r'^\s*(\d+)\s*/\s*(\d+)'
    input_string = re.sub(unknown_fraction_pattern, 
                           lambda x: str(float(Fraction(int(x.group(1)), int(x.group(2))))), 
                           input_string)

    # Regex pattern for single whole numbers at the start of the string (e.g., "2")
    whole_number_pattern = r'^\s*(\d+)(?=\s|$)'
    input_string = re.sub(whole_number_pattern, 
                           lambda x: str(int(x.group(1))), 
                           input_string)

    # Regex pattern for mixed fractions at the start of the string (e.g., "1 1/2")
    mixed_fraction_pattern = r'^\s*(\d+)\s+(\d+)\s*/\s*(\d+)'
    input_string = re.sub(mixed_fraction_pattern, 
                           lambda x: str(float(Fraction(int(x.group(1)) * int(x.group(3)) + int(x.group(2)), int(x.group(3))))), 
                           input_string)

    return input_string


for i in range(1,72):
    recipeList = str(f"https://thewoksoflife.com/category/recipes/page/{i}/")
    p = requests.get(recipeList) 

    soup = BeautifulSoup( p.content , 'html.parser')
    
    recipes = soup.find('main', class_='content flexbox').find_all('article')
    for recipe in recipes:
        try:
            URL = recipe.find('a').get('href')
            name = URL.split('/')[-2].replace('-', ' ').upper()
            
            page = requests.get(URL)
            soup = BeautifulSoup(page.content , 'html.parser') 

            print(URL)
            print(name)
            
            recipeTab = soup.find('div', class_='wprm-recipe-the-woks-of-life')
            groups = recipeTab.find_all( 'div', class_='wprm-recipe-ingredient-group')

            for group in groups:
                ings = group.find_all( 'li', class_='wprm-recipe-ingredient' )
                for i in ings:
                    try: amnt = i.find('span', class_='wprm-recipe-ingredient-amount').text
                    except: amnt = 'n/a'
                    try: unit = i.find('span', class_='wprm-recipe-ingredient-unit').text
                    except: unit = 'n/a'
                    try: name = i.find('span', class_='wprm-recipe-ingredient-name').text                  
                    except: name = 'n/a'
                    print(f";{convert_fractions_to_decimal(amnt)[0:6]};{unit};{name}")
                    
                    # Genrate embedding
            print("")
        except AttributeError:
            pass