
class Message:
    def __init__(self, type, node_id, key, value):
        self.type = type
        self.node_id = node_id
        self.key = key
        self.value = value
    
    def to_json(self):
        return json.dumps({
            "type": self.type,
            "node_id": self.node_id,
            "key": self.key,
            "value": self.value
        })

    