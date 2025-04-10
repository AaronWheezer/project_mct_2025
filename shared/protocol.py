import json

def make_message(action, data):
    return json.dumps({"action": action, "data": data})

def parse_message(message):
    return json.loads(message)
