
from dotenv import load_dotenv
import boto3
import json

query = "hello world"
region_name = 'us-east-1'

bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region_name=region_name)

response = bedrock_agent_runtime_client.retrieve_and_generate(
    input={
        "text": query
    },
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            'knowledgeBaseId': 'AOQJHDDKWV',
            "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/ai21.jamba-1-5-mini-v1:0",
            "retrievalConfiguration": {
                "vectorSearchConfiguration": {
                    "numberOfResults":5
                } 
            }
        }
    }
)

print(response['output']['text'],end='\n'*2)

print(response)