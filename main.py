# Import Module
import os
from bs4 import BeautifulSoup 
import requests 
from fractions import Fraction
import re
import json
import boto3
import logging
from botocore.exceptions import ClientError
import nanoid

# FRACTION TO DECIMAL helper
def fractions_to_decimal(input_string):
    # Dictionary mapping Unicode fractions to their decimal values
    fraction_map = {
        '¼': 0.25,
        '½': 0.5,
        '¾': 0.75,
        '⅐': 1/7,
        '⅑': 1/9,
        '⅒': 1/10,
        '⅓': 1/3,
        '⅔': 2/3,
        '⅕': 1/5,
        '⅖': 2/5,
        '⅗': 3/5,
        '⅘': 4/5,
        '⅙': 1/6,
        '⅚': 5/6,
        '⅛': 1/8,
        '⅜': 3/8,
        '⅝': 5/8,
        '⅞': 7/8
    }

    # Function to replace whole number and fraction with their decimal equivalent
    def replace_fraction(match):
        whole_number = match.group(1)  # Get the whole number
        fraction = match.group(2)        # Get the fraction
        
        # Convert fraction to decimal
        decimal_fraction = fraction_map.get(fraction, 0)
        
        # Combine whole number and decimal fraction
        if whole_number:
            return str(float(whole_number) + decimal_fraction)
        return str(decimal_fraction)
    # Regex to match optional whole numbers followed by a fraction
    output_string = re.sub(r'(\d+)?([¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])', replace_fraction, input_string)
    
    return output_string

# FIX MIXED helper
def fixMixed(input_string):
    try:
        st = input_string
        if input_string.find('-') != -1: st=st.split('-')[1].strip()
        parts = st.split(" ")
        if len(parts) == 1:
            if parts[0].find('/') == -1: return input_string
            else: return float(parts[0].split('/')[0]) / float(parts[0].split('/')[1])
        frac = []
        for p in parts:
            if p.find('/')!=-1:
                frac = p.split('/')
                return float(parts[0]) + float(frac[0])/float(frac[1])
        return float(parts[0]) + float(parts[1])
    except: return 1


def upload_file(contents, bucket, object_name=None):
    """Upload a file to an S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    print("Uploading file...")
    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.put_object(bucket, object_name, contents)
        print(response)
    except ClientError as e:
        logging.error(e)
        print(e)
        return False
    return True    

session = boto3.Session(aws_access_key_id='', aws_secret_access_key='')
s3 = session.resource('s3')

# RECIPE SCRAPING
for i in range(1,72):
    recipeList = str(f"https://thewoksoflife.com/category/recipes/page/{i}/")
    p = requests.get(recipeList)
    soup = BeautifulSoup( p.content , 'html.parser')
    chars = set('0123456789$,')
    # get all recipes
    recipes = soup.find('main', class_='content flexbox').find_all('article')
    for recipe in recipes:
        try:
            # URL ID and name
            URL = recipe.find('a').get('href')
            id = URL.split('/')[-2]
            name = id.replace('-', ' ')
            
            # html soup
            page = requests.get(URL)
            soup = BeautifulSoup(page.content , 'html.parser') 
            
            # storing raw text of recipe and ingredients
            recipeText = f"NAME: {name}\nURL: {URL}\nINGREDIENTS:\n"
            
            # finding the divs to scrape
            recipeTab = soup.find('div', class_='wprm-recipe-the-woks-of-life')
            groups = recipeTab.find_all( 'div', class_='wprm-recipe-ingredient-group')
            
            # print
            
            # storing ingredient components and ingredient embeddings in matrix for easier manipulating
            ingMatrix = [3*[]]
            
            # raw text of ingredients, plugged into titan for embed for the entire recipe
            ingsRawText = ""
            
            # looping through ingredient groups and ingredients
            for group in groups:
                ings = group.find_all( 'li', class_='wprm-recipe-ingredient' )
                
                # for each ingredient
                for i in ings:
                    
                    # attributes (amount)(unit)(name) being prettified and appended to matrix alongside their embedding
                    try: amnt = i.find('span', class_='wprm-recipe-ingredient-amount').text
                    except: amnt = '2'
                    try: unit = i.find('span', class_='wprm-recipe-ingredient-unit').text
                    except: unit = 'cups'
                    try: iname = i.find('span', class_='wprm-recipe-ingredient-name').text                  
                    except: iname = 'air'
                    
                    try: float(fixMixed(fractions_to_decimal(str(amnt))))
                    except: amnt = '2'
                    
                    ingMatrix.append([str(fixMixed(fractions_to_decimal(str(amnt)))), unit, iname])
                    # adding to rawtext
                    ingsRawText += f"{str(fixMixed(fractions_to_decimal(str(amnt))))},{unit},{iname}\n"
            
            # trimming first empty list element from declaration
            try: ingMatrix = ingMatrix[1:]
            except: pass
            recipeText += ingsRawText
            
            # finding instructions and appending to recipeText for full recipe embedding
            instructions = recipeTab.find('ul', class_='wprm-recipe-instructions').text
            recipeText += f"INSTRUCTIONS:\n{instructions}\n"
            
            print(recipeText)
            fileName = nanoid.generate(size=23) + ".txt"
            # print(fileName)
            # r = upload_file("core-hh-scheduler-builds", fileName, recipeText)
            # print(r)
            
            # s3_client.bucket("core-hh-scheduler-builds").put_object(Key=fileName, Body=recipeText)
            
            result = s3.Object('core-hh-scheduler-builds', fileName).put(Body=recipeText)
            
            # push commit after all inserts have been done for 1 recipe
        except AttributeError:
            pass # if code throws error, void the recipe and move on to next