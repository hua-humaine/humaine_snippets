import requests


# Endpoint: /logs/upload
# Method: POST
# Description: Upload a log file
def upload_log(api_url, log_file_path, config_id):
    endpoint = f"{api_url}/logs/upload"
    files = {'file': open(log_file_path, 'rb')}
    data = {'config_id': config_id}
    response = requests.post(endpoint, files=files, data=data)
    return response.json()


# Endpoint: /configuration/new
# Method: POST
# Description: Create a new configuration
def create_configuration(api_url, config_data):
    endpoint = f"{api_url}/configuration/new"
    response = requests.post(endpoint, json=config_data)
    return response.json()


# Endpoint: /evaluate/{configuration_id}
# Method: POST
# Description: Trigger the evaluation of a configuration
def evaluate_configuration(api_url, configuration_id):
    endpoint = f"{api_url}/evaluate/{configuration_id}"
    response = requests.post(endpoint)
    return response.json()


# Endpoint: /results/{configuration_id}
# Method: GET
# Description: Get the evaluation results of a configuration
def get_evaluation_results(api_url, configuration_id):
    endpoint = f"{api_url}/results/{configuration_id}"
    response = requests.get(endpoint)
    return response.json()
