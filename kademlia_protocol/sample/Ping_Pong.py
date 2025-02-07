import asyncio
import json
import random
import hashlib
import argparse

# For node (Node ID, IP, Port)
class Node:
    def __init__(self, node_id, ip, port):
        self.node_id = node_id
        self.ip = ip
        self.port = port
    
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
        try:
            message_obj = json.loads(message)
            msg_type = message_obj.get("type")
            if msg_type == "PING":
                self.handle_ping(message_obj, addr)
            elif msg_type == "PONG":
                self.handle_pong(message_obj, addr)
            else:
                print("Unknown message type")
        except json.JSONDecodeError:
            print("Invalid message format")

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

async def main():
    parser = argparse.ArgumentParser(description="Kademlia P2P node")
    parser.add_argument("--port", type=int, default=9999, help="Port number for the node")
    parser.add_argument('--peer-port', type=int, help='Port number of peer node')
    args = parser.parse_args()

    loop = asyncio.get_running_loop()

    node_id = hashlib.sha1(str(random.randint(0, 1000000)).encode()).hexdigest()
    port = args.port if args.port else 9999
    node = Node(node_id, "127.0.0.1", port)

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: KademliaProtocol(node),
        local_addr=(node.ip, node.port)
    )    
    protocol.connection_mode(transport)
    peer_port = args.peer_port if args.peer_port else 8888
    peer_address = ("127.0.0.1", peer_port)
    message = json.dumps({
        "type": "PING",
        "node_id": node.node_id
    })

    transport.sendto(message.encode(), peer_address)
    print(f"send Ping to [{peer_address}]")

    try: 
        await asyncio.sleep(100)
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())