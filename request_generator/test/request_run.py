import requests
import pickle

# payload1= {"user_id":1, "payload_size":[128, 128],"frequency":[2,1], "bandwidth":1000000,"app":["app1","app2"], "ms_chain":["2,service1-1-1,1-1","2,service1-1-1,2-1"]}

payload1= {"user_id":1, "payload_size":[128],"frequency":[0.2], "bandwidth":1000000,"app":["app1"], "ms_chain":["2,service1-1-1,1-1"]}


# remember to run "kubectl proxy" first
response = requests.post(url="http://127.0.0.1:8001/api/v1/namespaces/default/services/request-generator-service:2333/proxy/run", headers={"Content-Type": "application/json"},data=pickle.dumps(payload1))

print(pickle.loads(response.content))