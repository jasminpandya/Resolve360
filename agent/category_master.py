from typing import Any
from strands.types.tools import ToolResult, ToolUse
import boto3
import uuid
import yaml
import os

def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return None

TOOL_SPEC = {
    "name": "create_category",
    "description": "Create a new category in the category_master table in DynamoDB.",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "category_name": {
                    "type": "string",
                    "description": "The name of the category to be created."
                }
            },
            "required": ["category_name"]
        }
    }
}

def create_category(tool: ToolUse, **kwargs: Any) -> ToolResult:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'prereqs', 'prereqs_config.yaml')
    data = read_yaml_file(config_path)
    
    if not data:
        return {
            "toolUseId": tool["toolUseId"],
            "status": "error",
            "content": [{"text": "Failed to read prereqs_config.yaml"}]
        }

    kb_name = data.get('knowledge_base_name')
    if not kb_name:
        return {
            "toolUseId": tool["toolUseId"],
            "status": "error",
            "content": [{"text": "Missing 'knowledge_base_name' in config"}]
        }

    try:
        dynamodb = boto3.resource('dynamodb')
        smm_client = boto3.client('ssm')
        table_name_param = smm_client.get_parameter(
            Name=f'{kb_name}-category-table-name',
            WithDecryption=False
        )
        table_name = table_name_param["Parameter"]["Value"]
        table = dynamodb.Table(table_name)

        category_name = tool["input"]["category_name"]
        category_id = str(uuid.uuid4())[:8]

        print(f"Creating new category: {category_name} with ID {category_id}")

        table.put_item(
            Item={
                'category_id': category_id,
                'category_name': category_name
            }
        )

        return {
            "toolUseId": tool["toolUseId"],
            "status": "success",
            "content": [{"text": f"Category '{category_name}' created successfully with ID: {category_id}"}]
        }

    except Exception as e:
        return {
            "toolUseId": tool["toolUseId"],
            "status": "error",
            "content": [{"text": str(e)}]
        }
