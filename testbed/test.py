import requests
import pickle
import time

# payload1= {"user_id":1, "payload_size":[128, 128],"frequency":[2,1], "bandwidth":1000000,"app":["app1","app2"], "ms_chain":["2,service1-1-1,1-1","2,service1-1-1,2-1"]}

payload1= "2,service1-1-1,1-1"

begin = time.time_ns()
# remember to run "kubectl proxy" first
response = requests.post(url="http://127.0.0.1:8001/api/v1/namespaces/default/services/service1-1-1:5000/proxy/endpoint1", headers={"Content-Type": "application/json"},data=pickle.dumps(payload1))
elapsed = (time.time_ns() - begin) /1e6

print(pickle.loads(response.content))
print("Response time: ", elapsed, "ms")