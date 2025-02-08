import network.dht.routing as routing
import network.dht.node as node
import network.kademlia_protocol as kademlia
import hashlib
import asyncio
import argparse

async def main():
    parser = argparse.ArgumentParser(description="Kademlia P2P node")
    parser.add_argument("--port", type=int, help="Port number for the node")
    parser.add_argument("--message", type=str, help="Protocol type PING, FIND_NODE, STORE, FIND_VALUE")
    parser.add_argument("--bootstrap-node", type=str, help="Bootstrap Node", default="0x000000000000000000")
    args = parser.parse_args()

    loop = asyncio.get_running_loop()

    if args.bootstrap_node:
        bootstrap_node = node.Node(args.bootstrap_node.encode(), "127.0.0.1", 8000)
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: kademlia.KademliaProtocol(bootstrap_node),
            local_addr=(bootstrap_node.ip, bootstrap_node.port)
        )
        protocol.connection_mode(transport)

    try:
        await asyncio.sleep(10)
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())

    

