import os
import sys
import yaml

ms = sys.argv[1]
edge = sys.argv[2]

config_folder = "/home/rex/gitHub/cloud-native-app-simulator/testbed/k8s_converted/"

with open(config_folder+ms+".yaml", "r") as f:
    config = list(yaml.safe_load_all(f))

config[1]["spec"]["template"]["spec"]["nodeName"] = edge

with open(config_folder+ms+".yaml", "w") as f:
    yaml.dump_all(config, f)

os.system("kubectl apply -f "+config_folder+ms+".yaml")

