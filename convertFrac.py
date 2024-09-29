import re

# Function to convert fractions in strings to decimals
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