# Import Module
import os
from psycopg2 import pool
from dotenv import load_dotenv
from bs4 import BeautifulSoup 
import requests 
from fractions import Fraction
import re
import json
import boto3


# TITAN EMBEDDINGS V2 
class TitanEmbeddings(object):
    accept = "application/json"
    content_type = "application/json"
    
    def __init__(self, model_id="amazon.titan-embed-text-v2:0"):
        self.bedrock = boto3.client(service_name='bedrock-runtime')
        self.model_id = model_id
    def __call__(self, text, dimensions, normalize=True):
        """
        Returns Titan Embeddings
        Args:
            text (str): text to embed
            dimensions (int): Number of output dimensions.
            normalize (bool): Whether to return the normalized embedding or not.
        Return:
            List[float]: Embedding
        """
        body = json.dumps({
            "inputText": text,
            "dimensions": dimensions,
            "normalize": normalize
        })
        response = self.bedrock.invoke_model(
            body=body,
            modelId=self.model_id,
            accept=self.accept,
            contentType=self.content_type
        )
        response_body = json.loads(response.get('body').read())
        return response_body['embedding']
    
    def generate_embedding(self, text, dimensions, normalize=True):
        """
        Returns Titan Embeddings
        Args:
            text (str): text to embed
            dimensions (int): Number of output dimensions.
            normalize (bool): Whether to return the normalized embedding or not.
        Return:
            List[float]: Embedding
        """
        return self(text, dimensions, normalize)

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
            

# EMBED CONFIG
dimensions = 1024
normalize = True
tev2 = TitanEmbeddings(model_id="amazon.titan-embed-text-v2:0")

# NEON CONNECT
load_dotenv()
connection_string = 'postgresql://recipes_db_owner:hJQ1gMe3yBKD@ep-mute-smoke-a5r6kzr3.us-east-2.aws.neon.tech/recipes_db?sslmode=require'
connection_pool = pool.SimpleConnectionPool(1, 10, connection_string)
if connection_pool: print("Connection pool created successfully")
conn = connection_pool.getconn()


# CREATE CURSOR
cur = conn.cursor()


rCounter = 1
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
                    # titan call
                    #ingEmbed = tev2(f"{amnt},{unit},{iname}", dimensions, normalize)
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
            
            # titan embedding
            #recipeEmbed = tev2(recipeText, dimensions, normalize)
            #recipeText += f"{recipeEmbed}"
            
            print(recipeText)
            # push commit after all inserts have been done for 1 recipe
            conn.commit()
            rCounter+=1 # upping the counter to keep track of recipe id, PROBABLY BROKEN and part of the linker table issues
        except AttributeError:
            pass # if code throws error, void the recipe and move on to next


# CLOSE CONNECTION
cur.close()
connection_pool.putconn(conn)
connection_pool.closeall()