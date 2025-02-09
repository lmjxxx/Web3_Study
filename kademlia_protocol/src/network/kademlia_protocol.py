import asyncio
import network.dht.node as node
import json
import random
import hashlib

class KademliaProtocol(asyncio.DatagramProtocol):
    def __init__(self, node):
        self.node = node
        self.transport = None
        self.pending_pongs = {} # PING 을 보낸 후 그 응답을 기다리는 상태를 관리 key: node_id, value: asyncio.Future 객체

    def connection_made(self, transport):
        self.transport = transport
        self.node.transport = transport # Node - Transport 
        print(f"UDP server started at {self.node.ip}:{self.node.port}")

        self.node.routing_table.update(self.node)
        print(f"Node {self.node.node_id} added to its own routing table.")

        asyncio.create_task(self.send_periodic_ping())

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


    async def send_periodic_ping(self):
        # 주기적으로 라우팅 테이블에 있는 모든 녿에 PING 전송, 응답 확인
        while True:
            for bucket in self.node.routing_table.buckets:
                for node in bucket.nodes:
                    if node.node_id == self.node.node_id: # fix : 자기 자신은 건너 뜀
                        continue
                    await self.ping_node(node)
            await asyncio.sleep(30) # 30 초 마다 PING 전송

    async def wait_for_pong(self, node):
        # PONG 을 기다리는 Future 객체 
        future = asyncio.Future() # 비동기 작업의 결과를 표현하기 위해 사용
        self.pending_pongs[node.node_id] = future
        await future
        del self.pending_pongs[node.node_id]

    async def ping_node(self, node):
        # 특정 노드에 ping 전송
        ping_message = {"type": "PING", "node_id": self.node.node_id}
        self.transport.sendto(json.dumps(ping_message).encode(), (node.ip, node.port))
        print(f"Sent Ping to {node.ip}:{node.port}")

        try:
            # 5초 기다림
            await asyncio.wait_for(self.wait_for_pong(node), timeout=5)
            print(f"PONG received from {node.ip}:{node.port}")
        except asyncio.TimeoutError:
            # 응답이 없으면 노드 제거
            print(f"Node {node.node_id} did not respond. Removing from k-bucket")
            self.node.routing_table.remove(node)

    