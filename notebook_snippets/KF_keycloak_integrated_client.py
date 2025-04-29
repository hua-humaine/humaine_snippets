#from https://github.com/awslabs/kubeflow-manifests/issues/493

from keycloak import KeycloakOpenID
import os
import kfp
from kfp.client.set_volume_credentials import ServiceAccountTokenVolumeCredentials

# for kubeflow pipelines v1
# from kfp.auth import ServiceAccountTokenVolumeCredentials

# Keycloak configuration
keycloak_url = "<KEYCLOAK-URL>/realms"
client_id = "<KUBEFLOW-ID-AS-KEYCLOAK-CLIENT>"
client_secret = "<KUBEFLOW-SECRET-AS-KEYCLOAK-CLIENT>"

# User credentials
username = "<USERNAME_KEYCLOAK-USER>"
password = "<PASSWORD_KEYCLOAK-USER>"

# Initialize Keycloak client
kc_openid = KeycloakOpenID(server_url=keycloak_url,
                           client_id=client_id,
                           realm_name="<REALM_NAME>",
                           client_secret_key=client_secret)

# Authenticate and get the token
token = kc_openid.token(username, password)

# Extract the id_token
id_token = token['id_token']

# Save the id_token to a file (e.g., /tmp/token)
token_path = "/tmp/token"
with open(token_path, 'w') as token_file:
    token_file.write(id_token)

# Set the KF_PIPELINES_SA_TOKEN_PATH environment variable
os.environ['KF_PIPELINES_SA_TOKEN_PATH'] = token_path

# Initialize the KFP client
credentials = ServiceAccountTokenVolumeCredentials(path=None)
client = kfp.Client(host="<KF_PIPELINES_URL>", credentials=credentials)

print("Kubeflow Pipelines client initialized.")
