import requests
import pickle

payload1= {"user_id":1}

# Remember to run "kubectl proxy" first
response = requests.post(url="http://127.0.0.1:8001/api/v1/namespaces/default/services/request-generator-service:2333/proxy/stop", headers={"Content-Type": "application/json"},data=pickle.dumps(payload1))

print(pickle.loads(response.content))