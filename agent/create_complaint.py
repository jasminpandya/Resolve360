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
    "name": "create_complaint",
    "description": "Raise a new complaint for a customer in the system and store it in the database.",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": """The user ID of the customer raising the complaint.
                    This should be a unique identifier for the user."""
                },
                "description": {
                    "type": "string",
                    "description": "The description of the complaint being raised by the user in plain text"
                }
            },
            "required": ["client_id", "description"]
        }
    }
}
# Function name must match tool name
import os

def create_complaint(tool: ToolUse, **kwargs: Any) -> ToolResult:
    # get the knowledge base name from the prereqs_config.yaml file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = f'{current_dir}/prereqs/prereqs_config.yaml'
    data = read_yaml_file(config_path)
    kb_name = data['knowledge_base_name']
    dynamodb = boto3.resource('dynamodb')
    smm_client = boto3.client('ssm')
    table_name = smm_client.get_parameter(
        Name=f'{kb_name}-table-name',
        WithDecryption=False
    )
    table = dynamodb.Table(table_name["Parameter"]["Value"])
    
    tool_use_id = tool["toolUseId"]
    client_id = tool["input"]["client_id"]
    description = tool["input"]["description"]
    
    results = f"Raising complaint for user {client_id} with description: {description}"

    print(results)
    try:
        complaint_id = str(uuid.uuid4())[:8]
        table.put_item(
            Item={
                'complaint_id': complaint_id,
                'description': description,
                'client_id': client_id,
                'status': 'open'   # Assuming a status field to track the complaint status 
            }
        )
        return {
            "toolUseId": tool_use_id,
            "status": "success",
            "content": [{"text": f"Complaint raised successfully with ID: {complaint_id}"}]
        } 
    except Exception as e:
        return {
            "toolUseId": tool_use_id,
            "status": "error",
            "content": [{"text": str(e)}]
        } 
