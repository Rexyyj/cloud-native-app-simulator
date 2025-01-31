import requests
import threading
from queue import Queue
import cherrypy
from pymongo import MongoClient
import string, random
import time
import pickle
import numpy as np
import os
# ms_chains structure "2,MS1-1-1,1-2"
# First MS full name <name>-<quality>-<instance>
# Following MS only <quality>-<instance>
# payload_size, frequency, ms_chains are list
class USER:
    def __init__(self, id, payload_size,frequencys, bandwidth,apps,entry_points,ms_chains):
        self.id = id
        self.payload_size = payload_size
        self.frequency = frequencys
        self.counter = np.zeros(len(apps))
        self.time_out = 10
        self.ms_chains = ms_chains
        self.bandwidth = bandwidth
        self.header = {"Content-Type": "application/json"} 
        self.apps = apps
        self.entry_points = entry_points
        self.edge_id = int(os.environ.get('EDGE_ID', '0'))

        self.head_ms =[]
        for ms in ms_chains:
            self.head_ms.append(ms.split(",")[1])

        self.number_of_workers =0
        for i in range(len(apps)):
            self.number_of_workers+= frequencys[i]
        if self.number_of_workers<1:
            self.number_of_workers = 1

        self.thread_pool =[]
        # Queue to hold tasks
        self.task_queue = Queue(maxsize=20)

        self.client = MongoClient("mongodb://mongodb:27017/")
        self.db = self.client["test_database"]
        self.collection = self.db["test_collection"]
        # self.is_running = False
        self.stop_event = threading.Event()
        self.run()

    def update_configuration(self, config):
        self.payload_size=config["payload_size"]
        self.frequency = config["frequency"]
        self.bandwidth = config["bandwidth"]
        self.ms_chains = config["ms_chain"]

    def update_bandwidth(self, bw):
        self.bandwidth = bw


    def run(self):
        for i in range(self.number_of_workers):
            t = threading.Thread(target=self.worker)
            t.start()
            self.thread_pool.append(t)
        for j in range(len(self.apps)):
            t2 = threading.Thread(target=self.producer,args=(j,))
            t2.start()
            self.thread_pool.append(t2)

    def stop(self):
        self.stop_event.set()
        for t in self.thread_pool:
            if t.is_alive():
                t.join(timeout=0.1)
        # Drain the queue (allow workers to finish processing)
        self.task_queue.join()


    # Function to send a POST request
    def send_post_request(self, counter, app):
        try:
            url = "http://%s/%s" % (self.head_ms[app],self.entry_points[app])
            payload = self.ms_chains[app]+"/"+''.join(random.choices(string.ascii_letters, k=self.payload_size[app]-len(self.ms_chains[app])-1))

            begin_time = time.time_ns()
            user_edge_delay = self.payload_size[app] * 8 / self.bandwidth
            time.sleep(user_edge_delay)
            try:
                _ = requests.post(url, data=payload, headers=self.header, timeout=self.time_out)
                # print("Created a post \n url: %s \n ms_chain: %s" % (url, self.ms_chains[app]))
            except requests.exceptions.Timeout:
                # Handle timeout exception
                print(f"Request timed out after {self.time_out} seconds.")
            except requests.exceptions.RequestException as e:
                # Handle other request exceptions
                print(f"An error occurred: {e}")
            elapsed_time = (time.time_ns() - begin_time) / 1e6

            measurement = {"user_id":self.id,"app":self.apps[app],"entry":self.entry_points[app] ,"edge":self.edge_id,"time":begin_time ,"counter":counter, "latency":elapsed_time, "payload_size":self.payload_size[app], "freq":self.frequency[app] }
            # print("Insert one measurement to DB: ", measurement)
            self.collection.insert_one(measurement)
        except Exception as e:
            print(f"Error: {e}")

    # Worker function to process requests from the queue
    def worker(self):
        while not self.stop_event.is_set():
            task = self.task_queue.get()
            if task is None:
                break  # Exit the worker
            self.send_post_request(counter=task["counter"], app=task["app"])
            self.task_queue.task_done()

    def producer(self, app):
        interval = 1 / self.frequency[app]
        while not self.stop_event.is_set():
            print("Producer %d running" % app)
            # Add task to the queue
            self.counter[app]+=1
            self.task_queue.put({"counter": self.counter[app], "app":app})
            time.sleep(interval)  # Control the frequency accurately

class REQGEN:
    exposed = True
    @cherrypy.tools.accept(media='text/plain')
    def __init__(self) -> None:
        self.user_dict = {}
       
    
    #{"user_id":1, payload_size:[](bytes),frequency:[] (Hz), bandwidth:10000 (bps),"app":[], ms_chian: []"2,MS1-1-1,1-2"}
    def POST(self, *uri):
        if uri[0] == "run":
            body = cherrypy.request.body.read()
            data = pickle.loads(body)
            print(self.user_dict)
            try: 
                user = self.user_dict[data["user_id"]]
                user.update_configuration(data)
                response = {"status":"User updated"}
            except  Exception as e:
                print(f"Error: {e}")
                user = USER(id=data["user_id"],
                            payload_size=data["payload_size"],
                            frequencys=data["frequency"],
                            bandwidth=data["bandwidth"],
                            apps=data["app"],
                            entry_points=data["entry_point"],
                            ms_chains=data["ms_chain"])
                self.user_dict[data["user_id"]] = user
                response = {"status":"User created"}
            return pickle.dumps(response)
        
        if uri[0] == "updateBW":
            body = cherrypy.request.body.read()
            data = pickle.loads(body)
            try:
                user = self.user_dict[data["user_id"]]
                user.update_bw(data["bandwidth"])
                response = {"status":"User bw updated"}
            except:
                response = {"status":"User not exist"}
            return pickle.dumps(response)

        if uri[0] == "stop":
            body = cherrypy.request.body.read()
            data = pickle.loads(body)
            try:
                user = self.user_dict[data["user_id"]]
                user.stop()
                del self.user_dict[data["user_id"]]
                response = {"status":"User removed"}
            except:
                response = {"status":"User not exist"}

            return pickle.dumps(response)




if __name__ == "__main__":

    request_generator = REQGEN()
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')]
        }
    }
    # set this address to host ip address to enable dockers to use REST api
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.config.update(
        {'server.socket_port':2333 })

    # Blocking the terminal and show output, for debug
    cherrypy.tree.mount(request_generator, "/",conf)
    cherrypy.engine.start()
    cherrypy.engine.block()