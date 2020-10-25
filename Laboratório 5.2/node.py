import sys
import rpyc
import hashlib
import json

from rpyc.utils.server import ThreadedServer

class Node(rpyc.Service):

    def __init__(self, id):
        self.id = id
        self.table_entries = {}
    
    def set_address(self, address):
        self.address = address

    def set_ring_address(self, address):
        self.ring_address = address

    def set_n(self, n):
        self.n = n
    
    def register_to_ring(self):
        (host, port) = self.ring_address
        ring = rpyc.connect(host, port)
        ring.root.register_node(self.id, self.address)
        ring.close()

    def closest_preceding_node(self, id):
        for finger in reversed(self.finger_table):
            if id < self.id and ((finger['id'] > self.id and finger['id'] <= 2**self.n) or (finger['id'] >= 0 and finger['id'] < id)):
                return finger
            elif finger['id'] > self.id and finger['id'] < id:
                return finger
        return {'id': self.id, 'address': self.address}

    def exposed_set_successor(self, successor):
        self.successor = json.loads(successor)

    def exposed_set_finger_table(self, finger_table):
        self.finger_table = json.loads(finger_table)

    def exposed_save_entry(self, key, value):
        self.table_entries[key] = value
        print(f'Chave/valor inseridos no nó {self.id}')

    def exposed_return_value(self, key):
        value = self.table_entries.get(key)
        (host, port) = self.ring_address
        ring = rpyc.connect(host, port)
        ring.root.search_return(value)
        ring.close()

    def exposed_insert(self, key, value, id=None):
        if id == None:
            key_hash = hashlib.sha256()
            key_bytes = key.encode()
            key_hash.update(key_bytes)
            id = int(key_hash.hexdigest(), 16) % (2**self.n)
        if id == self.id:
            self.exposed_save_entry(key, value)
            return
        successor = self.successor
        if successor['id'] < self.id and ((id > self.id and id <= 2**self.n) or (id >= 0 and id <= successor['id'])):
            (host, port) = successor['address']
            node = rpyc.connect(host, port)
            node.root.save_entry(key, value)
            node.close()
        elif id > self.id and id <= successor['id']:
            (host, port) = successor['address']
            node = rpyc.connect(host, port)
            node.root.save_entry(key, value)
            node.close()

        else:
            closest_preceding_node = self.closest_preceding_node(id)
            (host, port) = closest_preceding_node['address']
            node = rpyc.connect(host, port)
            node.root.insert(key, value, id)
            node.close()
        
    def exposed_search(self, key, id=None):
        if id == None:
            key_hash = hashlib.sha256()
            key_bytes = key.encode()
            key_hash.update(key_bytes)
            id = int(key_hash.hexdigest(), 16) % (2**self.n)
        if id == self.id:
            self.exposed_return_value(key)
            return
        successor = self.successor
        if successor['id'] < self.id and ((id > self.id and id <= 2**self.n) or (id >= 0 and id <= successor['id'])):
            (host, port) = successor['address']
            node = rpyc.connect(host, port)
            node.root.return_value(key)
            node.close()
        elif id > self.id and id <= successor['id']:
            (host, port) = successor['address']
            node = rpyc.connect(host, port)
            node.root.return_value(key)
            node.close()

        else:
            closest_preceding_node = self.closest_preceding_node(id)
            (host, port) = closest_preceding_node['address']
            node = rpyc.connect(host, port)
            node.root.search(key, id)
            node.close()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit('Faltando parâmetros para iniciar o nó')
    
    n = int(sys.argv[1])
    id = int(sys.argv[2])
    ring_address = (sys.argv[3], int(sys.argv[4]))

    node = Node(id)
    server = ThreadedServer(node)

    node.set_n(n)
    node.set_address((server.host, server.port))
    node.set_ring_address(ring_address)
    node.register_to_ring()

    server.start()

    


