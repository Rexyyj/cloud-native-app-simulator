import os
import sys
import yaml

ms = sys.argv[1]

config_folder = "/home/rex/gitHub/cloud-native-app-simulator/testbed/k8s_converted/"


os.system("kubectl delete -f "+config_folder+ms+".yaml")

with open(config_folder+ms+".yaml", "r") as f:
    config = list(yaml.safe_load_all(f))

config[1]["spec"]["template"]["spec"]["nodeName"] = "dummy"

with open(config_folder+ms+".yaml", "w") as f:
    yaml.dump_all(config, f)