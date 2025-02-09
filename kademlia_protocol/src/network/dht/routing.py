class KBucket:
    def __init__(self, range_min,range_max, k=20):
        self.random_min = range_min # min range
        self.range_max = range_max # max range 
        self.k = k
        self.nodes = [] # list of nodes

    def in_range(self, node_id_int):
        return self.range_min <= node_id_int < self.range_max

    def add_node(self, node):
        for n in self.nodes:
            if n.node_id == node.node_id:
                n.update_timestamp()
                return
        if len(self.nodes) < self.k: 
            self.nodes.append(node)
        else:
            # bucket full, check old node 
            # todo : change node before ping check
            oldest_node = min(self.nodes, key=lambda n: n.last_seen)
            self.nodes.remove(oldest_node)
            self.nodes.append(node)


class RoutingTable:
    def __init__(self, local_node_id, k=20, id_bits=160):
        self.local_node_id = local_node_id
        self.k = k
        self.id_bits = id_bits
        # bucket[i] : xor [2**i, 2**(i+1)]
        self.buckets = []
        for i in range(self.id_bits):
            range_min = 2 ** i
            range_max = 2 ** (i+1)
            self.buckets.append(KBucket(range_min, range_max))
    
    def remove(self, node):
        # 라우팅 테이블에서 특정 노드 제거
        bucket_idx = self.bucket_idx(node.node_id)
        bucket = self.buckets[bucket_idx]
        bucket.nodes = [n for n in bucket.nodes if n.node_id != node.node_id]
        print(f"Remove node {node.node_id} from bucket {bucket_idx}")

    def chk_bucket(self):
        # change : 값이 있는 버킷만 출력
        for i, bucket in enumerate(self.buckets):
            if len(bucket.nodes) > 0:
                print(f"KBucket {i}: Node = Count = {len(bucket.nodes)}")
                for node in bucket.nodes:
                    print(f"    Node ID: {node.node_id}, IP: {node.ip}, Port: {node.port}")

    def xor_distance(self, id1, id2):
        # id1, id2 : hex string
        return int(id1, 16) ^ int(id2, 16)

    def bucket_idx(self, node_id):
        distance = self.xor_distance(self.local_node_id, node_id)
        if distance == 0:
            return 0 # local node
        
        idx = distance.bit_length() - 1
        return idx
    
    def update(self, node):
        idx = self.bucket_idx(node.node_id)
        if idx is None:
            return 
        self.buckets[idx].add_node(node)

    def find_closest(self, target_id, count=5):
        all_nodes = []
        for bucket in self.buckets:
            all_nodes.extend(bucket.nodes)

        # sort by xor distance
        all_nodes.sort(key=lambda n: self.xor_distance(n.node_id, target_id))
        return all_nodes[:(count or self.k)]



