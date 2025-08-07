from typing import Any
from strands.types.tools import ToolResult, ToolUse
import boto3
import uuid
import yaml

def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return None

TOOL_SPEC = {
    "name": "create_person_master",
    "description": "Person master table",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "person_id": {
                    "type": "string",
                    "description": """The person ID of individual working on complaint.
                    This should be a unique identifier."""
                },
                "person_name": {
                    "type": "string",
                    "description": "Name of the individual/Person"
                },

                "person_email": {
                    "type": "string",
                    "description": "Email Id of the individual/Person"
                },

                "person_type": {
                    "type": "string",
                    "description": "Person type of individual, it may be client|advisory|support|admin"
                },

                "category_id": {
                    "type": "string",
                    "description": "Category ID of individual"
                },

            },
            "required": ["person_id", "person_name", "person_email"]
        }
    }
}
# Function name must match tool name
import os

def create_person(tool: ToolUse, **kwargs: Any) -> ToolResult:
    # get the knowledge base name from the prereqs_config.yaml file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = f'{current_dir}/prereqs/prereqs_config.yaml'
    data = read_yaml_file(config_path)
    kb_name = data['knowledge_base_name']
    dynamodb = boto3.resource('dynamodb')
    smm_client = boto3.client('ssm')
    table_name = smm_client.get_parameter(
        Name=f'{kb_name}-person_table_name',
        WithDecryption=False
    )
    table = dynamodb.Table(table_name["Parameter"]["Value"])
    
    tool_use_id = tool["toolUseId"]
    person_id = tool["input"]["person_id"]
    person_name = tool["input"]["person_name"]
    person_email= tool["input"]["person_email"]
    person_type= tool["input"]["person_type"]
    category_id= tool["input"]["category_id"]
    
    results = f"creating person-master table with person_id: {person_id} person_name: {person_name} person_email: {person_email}"

    print(results)
    try:
        person_id = str(uuid.uuid4())[:8]
        table.put_item(
            Item={
                'person_id': person_id,
                'person_name': person_name,
                'person_email': person_email,
                'person_type': person_type,
                'category_id' : category_id
            }
        )
        return {
            "toolUseId": tool_use_id,
            "status": "success",
            "content": [{"text": f" person  added successfully with ID: {person_id}"}]
        } 
    except Exception as e:
        return {
            "toolUseId": tool_use_id,
            "status": "error",
            "content": [{"text": str(e)}]
        } 
