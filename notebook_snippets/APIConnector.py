import requests
import kfp

HOST = 'http://10.100.59.230:31973'
USERNAME = "user@example.com"
PASSWORD = "12341234"
NAMESPACE = "kubeflow-user-example-com"

session = requests.Session()
response = session.get(HOST)

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

data = {"login": USERNAME, "password": PASSWORD}
session.post(response.url, headers=headers, data=data)
session_cookie = session.cookies.get_dict()["authservice_session"]

client = kfp.Client(
    host=f"{HOST}/pipeline",
    cookies=f"authservice_session={session_cookie}",
    namespace=NAMESPACE,
)

print(session_cookie)
 

# test that we have a valid session
#print(client.list_pipelines())
print(client.get_user_namespace())
print(client.get_recurring_run("2fc815d5-6861-4241-b3d6-5bcdb5445b0b"))
