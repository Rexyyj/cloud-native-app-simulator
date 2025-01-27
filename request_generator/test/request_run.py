import requests
import pickle

payload1= {"user_id":1, "payload_size":[128, 128],"frequency":[2,1], "bandwidth":1000000,"app":["app1","app2"], "ms_chain":["2,ms1-1-1,1-2,1-3","2,ms2-1-1,1-2,1-3"]}

response = requests.post(url="http://192.168.0.110:2356/run", headers={"Content-Type": "application/json"},data=pickle.dumps(payload1))

print(pickle.loads(response.content))