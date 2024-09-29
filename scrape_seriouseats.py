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

text = open('seriousEatsLinks.txt', 'r')
textList = text.readlines()

for textLine in textList:
    try:
        splitLine = textLine.split(', ')
        name = splitLine[0].upper()
        URL = splitLine[1]
        
        print(URL)
        print(name)
        
        page = requests.get(URL)
        soup = BeautifulSoup(page.content , 'html.parser')
        
        recipeTab = soup.find('div', class_='comp structured-ingredients')
        ings = recipeTab.find_all('li', class_='structured-ingredients__list-item')
        for i in ings:
            components = i.find_all('span')
            for c in components:
                if len(components) == 3:
                    if any(i.isdigit() for i in components[0].text):
                        amount = components[0].text
                        unit = components[1].text
                        name = components[2].text
                    else:
                        name = components[0].text
                        amount = components[1].text
                        unit = components[2].text
                else:
                    name = components[0].text
                    amount = 'n/a'
                    unit = 'n/a'
            print(f";{convert_fractions_to_decimal(amount)[0:6]};{unit};{name}")
        print()
    except AttributeError:
        pass

text.close()