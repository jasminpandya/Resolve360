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
def delete_person(person_id: str) -> str:
    """Delete a complaint by its ID and client ID.
    Args: 
        person_id (str): The ID of the person to delete.
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
        Name=f'{kb_name}-person_table_name',
        WithDecryption=False
    )
    table = dynamodb.Table(table_name["Parameter"]["Value"])
    try:
        response = table.delete_item(Key={'person_id': person_id})
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return f'Person with ID {person_id} deleted successfully.'
        else:
            return f'Failed to delete Person with ID {person_id}.'
    except Exception as e:
        return str(e)
