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
def get_person_details(person_id:str) -> dict:
    """Get the details of person by its ID and category ID.
    Args: 
        person_id (str): The ID of the person to retrieve.
    Returns:
        dict: A dictionary containing the user details or an error message.
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
        response = table.get_item(
            Key={
                'person_id': person_id
            }
        )
        if 'Item' in response:
            return response['Item']
        else:
            return f'No person found with ID {person_id}.'
    except Exception as e:
        return str(e)
