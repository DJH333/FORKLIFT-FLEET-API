import json

def load_forklift_data():
    with open("forklift_data.json", "r") as file:
        forklifts = (json.load(file))
    return forklifts