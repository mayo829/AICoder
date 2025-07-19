import importlib
import json
import os

def load_agent_nodes(contract_folder="contracts"):
    nodes = {}
    for file in os.listdir(contract_folder):
        if not file.endswith(".agent.json"):
            continue
        with open(os.path.join(contract_folder, file)) as f:
            config = json.load(f)
            module = importlib.import_module(config["path"])
            node = getattr(module, config["entrypoint"])
            nodes[config["name"]] = node
    return nodes
