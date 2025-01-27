import requests
import pickle

payload1= {"user_id":1, "payload_size":[128, 128],"frequency":[2,1], "bandwidth":1000000,"app":["app1","app2"], "ms_chain":["2,service1-1-1,1-1","2,service1-1-1,2-1"]}

response = requests.post(url="http://localhost:2333/run", headers={"Content-Type": "application/json"},data=pickle.dumps(payload1))

print(pickle.loads(response.content))