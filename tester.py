# Import Module 
from bs4 import BeautifulSoup 
import requests 
from fractions import Fraction
import re
import json
import boto3

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

dimensions = 1024
normalize = True
    
titan_embeddings_v2 = TitanEmbeddings(model_id="amazon.titan-embed-text-v2:0")

input_text = "What are the different services that you offer?"
embedding = titan_embeddings_v2(input_text, dimensions, normalize)