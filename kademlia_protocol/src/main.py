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
    parser.add_argument("--ip", type=str, help="IP", default="127.0.0.1")
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

    elif args.port and args.message:
        # new node
        # bootstrap_node에 FIND_NODE 메시지를 보내서 가까운 노드 목록을 반환 받아 자신의 k-bucket 에 추가하는 것 구현
        new_node = node.Node(hashlib.sha1(f"{ip}{port}"), args.ip.encode(), args.port)
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: kademlia.KademliaProtocol(new_node),
            local_addr=(new_node.ip, args.port)
        )

        find_node_request = {
            "type": "FIND_NODE",
            "sendor_id": new_node.node_id,
            "target_id": "0x000000000000000000" # bootstrap_node
        }
        new_node.transport.sendto(json.dumps(find_node_request).encode(), (new_node.ip, new_node.port))

    try:
        await asyncio.sleep(10)
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())

    

