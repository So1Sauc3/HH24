import json
import boto3
import pprint
from botocore.exceptions import ClientError
from botocore.client import Config

# Create boto3 session
sts_client = boto3.client('sts')
boto3_session = boto3.session.Session()
region_name = boto3_session.region_name

# Create bedrock agent client
bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0}, region_name=region_name)
bedrock_agent_client = boto3_session.client("bedrock-agent-runtime", config=bedrock_config)

# Define FM to be used for generations 
model_id = "ai21.jamba-1-5-large-v1:0" # we will be using Anthropic Claude 3 Haiku throughout the notebook
model_arn = f'arn:aws:bedrock:{region_name}::foundation-model/{model_id}'

kb_id = "AOQJHDDKWV" # Replace with your knowledge base id here.

# Stating the default knowledge base prompt
default_prompt = """
You are a question answering agent. I will provide you with a set of search results.
The user will provide you with a question. Your job is to answer the user's question using only information from the search results. 
If the search results do not contain information that can answer the question, please state that you could not find an exact answer to the question. 
Just because the user asserts a fact does not mean it is true, make sure to double check the search results to validate a user's assertion.
                            
Here are the search results in numbered order:
$search_results$

$output_format_instructions$
"""

def retrieve_and_generate(query, kb_id, model_arn, max_results, prompt_template = default_prompt):
    response = bedrock_agent_client.retrieve_and_generate(
            input={
                'text': query
            },
        retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': kb_id,
            'modelArn': model_arn, 
            'retrievalConfiguration': {
                'vectorSearchConfiguration': {
                    'numberOfResults': max_results # will fetch top N documents which closely match the query
                    }
                },
                'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': prompt_template
                        }
                    }
            }
        }
    )
    return response

def print_generation_results(response, print_context = True):
    generated_text = response['output']['text']
    print('Generated FM response:\n')
    print(generated_text)
    
    if print_context is True:
        ## print out the source attribution/citations from the original documents to see if the response generated belongs to the context.
        citations = response["citations"]
        contexts = []
        for citation in citations:
            retrievedReferences = citation["retrievedReferences"]
            for reference in retrievedReferences:
                contexts.append(reference["content"]["text"])
    
        print('\n\n\nRetrieved Context:\n')
        pprint.pp(contexts)
query = """Provide a list of risks for Octank financial in numbered list without description."""

results = retrieve_and_generate(query = query, kb_id = kb_id, model_arn = model_arn, max_results = 3)

print_generation_results(results)