
class Node:
    def __init__(self, node_id, ip, port):
        self.node_id = node_id
        self.ip = ip
        self.port = port 
        self.last_seen = last_seen or time.time()
        self.routing_table = {}
        self.protocol = None
        self.transport = None
    def update_timestamp(self):
        self.last_seen = time.time()