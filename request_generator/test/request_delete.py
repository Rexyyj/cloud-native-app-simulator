import requests
import pickle

payload1= {"user_id":1}

response = requests.post(url="http://localhost:2333/stop", headers={"Content-Type": "application/json"},data=pickle.dumps(payload1))

print(pickle.loads(response.content))