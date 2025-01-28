import requests
import pickle
import time


payload1= "2,service1-1-1,1-1"
payload1= "2,service1-1-1,2-1"

begin = time.time_ns()
# remember to run "kubectl proxy" first
response = requests.post(url="http://127.0.0.1:8001/api/v1/namespaces/default/services/service1-1-1:80/proxy/endpoint1", data=payload1)
elapsed = (time.time_ns() - begin) /1e6

print(pickle.loads(response.content))
print("Response time: ", elapsed, "ms")