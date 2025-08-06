from strands import tool
import boto3 
import yaml
import os

def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return None

@tool
def delete_booking(complaint_id: str, client_id:str) -> str:
    """Delete a complaint by its ID and client ID.
    Args: 
        complaint_id (str): The ID of the complaint to delete.
        client_id (str): The ID of the client who raised the complaint.
    Returns:
        str: A message indicating the result of the deletion operation.
    """
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
    try:
        response = table.delete_item(Key={'complaint_id': complaint_id, 'client_id': client_id})
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return f'Complaint with ID {complaint_id} for client {client_id} deleted successfully.'
        else:
            return f'Failed to delete complaint with ID {complaint_id} for client {client_id}.'
    except Exception as e:
        return str(e)
