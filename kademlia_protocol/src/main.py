import network.dht.routing as routing
import network.dht.node as node
import network.protocol as protocol 
import hashlib
import asyncio
import argparse

async def main():
    parser = argparse.ArgumentParser(description="Kademlia P2P node")
    parser.add_argument("--port", type=int, help="Port number for the node")
    parser.add_argument("--message", type=str, help="Protocol type PING, FIND_NODE, STORE, FIND_VALUE")
    parser.add_argument("--bootstrap-node", type=str, help="Bootstrap Node")
    args = parser.parse_args()

    loop = asyncio.get_running_loop()

    if args.bootstrap_node:
        bootstrap_node = node.Node(int(args.bootstrap_node, 16), "127.0.0.1", 8000)
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: protocol.KademliaProtocol(bootstrap_node),
            local_addr=(bootstrap_node.ip, bootstrap_node.port)
        )
        protocol.connection_mode(transport)
    

if __name__ == "__main__":
    asyncio.run(main())
