# p2p basic 
    * Python 
    * asyncio : asynchronous I/O, event Loop
    * sockt, asyncio Datagram Protocol : for UDP
    * json : message serialization, deserialization

    * kademlia_protocol
        - Kademlia DHT Protocol

    ## 1. message
        ### PING 
            ```
            {
                "type": "PING",
                "node_id": node_id
            }
            ```
        ### PONG 
            { 
                "type": "PONG",
                "node_id": "node_id
            }

        ### FIND_NODE
            {
                "type": "FIND_NODE",
                "sendor_id": "0xaaaabbbbccccffff...",
                "target_id": "0x1111222233334444...",
            }
        
        ### FIND_NODE response NODE_LIST
            { 
                "type": "NODE_LIST",
                "nodes": [
                    {"node_id": "0x12345...", "ip": "127.0.0.1", "port": 8001},
                    {"node_id": "0x67889...", "ip": "127.0.0.1", "port": 8002}
                    ...
                ]
            }
        
        ### STORE
            todo
        
        ### FIND_VALUE
            todo