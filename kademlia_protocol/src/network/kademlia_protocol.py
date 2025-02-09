import asyncio
import network.dht.node as node
import json
import random
import hashlib

class KademliaProtocol(asyncio.DatagramProtocol):
    def __init__(self, node):
        self.node = node
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.node.transport = transport # Node - Transport 
        print(f"UDP server started at {self.node.ip}:{self.node.port}")

        self.node.routing_table.update(self.node)
        print(f"Node {self.node.node_id} added to its own routing table.")

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"received [{addr}]: {message}")
        try:
            message_obj = json.loads(message)
            msg_type = message_obj.get("type")
            if msg_type == "FIND_NODE":
                self.handle_find_node(message_obj, addr)
            elif msg_type == "NODE_LIST":
                self.handle_node_list(message_obj)
            elif msg_type == "PING":
                self.handle_ping(message_obj, addr)
            elif msg_type == "PONG":
                self.handle_pong(message_obj, addr)
            elif msg_type == "STORE":
                self.handle_store(message_obj, addr)
            elif msg_type == "FIND_VALUE":
                self.hadnel_find_value(message_obj, addr)
            else:
                print("Unknown message type.")
            
        except json.JSONDecodeError:
            print("Invalid JSON format.")
            

    def handle_ping(self, message, addr):
        # pong 
        response = json.dumps({
            "type": "PONG",
            "node_id": self.node.node_id
        })
        self.transport.sendto(response.encode(), addr)
        print(f"send [{addr}]: {response}")

    def handle_pong(self, message, addr):
        print(f"PONG received from {addr}, Node ID : {message.get("node_id")}")

    def handle_find_node(self, message, addr):
        # todo
        sendor_id = message["sendor_id"]
        print(f"FIND_NODE received from {addr}, Node ID : {message.get("node_id")}")

        new_node = node.Node(sendor_id, addr[0], addr[1])
        self.node.routing_table.update(new_node)
        print(f"Added {new_node.node_id} to local k-bucket.")

        target_id = message["target_id"]
        closest_nodes = self.node.routing_table.find_closest(target_id, count=5) # Node's Routing Table

        response = {
            "type": "NODE_LIST",
            "nodes": [{"node_id": n.node_id, "ip": n.ip, "port":n.port} for n in closest_nodes]
        }
        
        self.transport.sendto(json.dumps(response).encode(), addr)
        print(f"Sent NODE_LIST to {json.dumps(response)}")

    def handle_node_list(self, message):
        # NODE_LIST message : 받은 노드들을 k-bucket에 추가
        nodes = message["nodes"]
        for node_info in nodes:
            new_node = node.Node(node_info["node_id"], node_info["ip"], node_info["port"])
            self.node.routing_table.update(new_node) # Node 의 라우팅 테이블에 새 노드 추가
            print(self.node.routing_table)
        print(self.node.routing_table.chk_bucket())
        
    
    def handle_store(self, message, addr):
        # todo
        print(f"STORE received from {addr}, Node ID : {message.get("node_id")}")
    
    def handle_find_value(self, message, addr):
        # todo
        print(f"FIND_VALUE received from {addr}, Node ID : {message.get("node_id")}")

