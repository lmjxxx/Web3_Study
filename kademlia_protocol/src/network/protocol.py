import asyncio
import json
import random
import hashlib

class KademliaProtocol(asyncio.DatagramProtocol):
    def __init__(self, node):
        self.node = node
        self.transport = None

    def connection_mode(self, transport):
        self.transport = transport
        print(f"UDP server started at {self.node.ip}:{self.node.port}")

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"received [{addr}]: {message}")

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
        print(f"FIND_NODE received from {addr}, Node ID : {message.get("node_id")}")
    
    def handle_store(self, message, addr):
        # todo
        print(f"STORE received from {addr}, Node ID : {message.get("node_id")}")
    
    def handle_find_value(self, message, addr):
        # todo
        print(f"FIND_VALUE received from {addr}, Node ID : {message.get("node_id")}")

