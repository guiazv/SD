import sys
import os
import signal
import subprocess
import rpyc
import socket
import threading
import json

from rpyc.utils.server import ThreadedServer

class NodeRing(rpyc.Service):
    def __init__(self, n):
        self.n = n
        self.max_nodes = 2**n
        self.nodes = {}

    def set_address(self, address):
        self.address = address

    def spawn_node(self, node_id):
        (host, port) = self.address
        subprocess.Popen(['python3', 'node.py', str(n),str(node_id), host, str(port)], shell=False)
    
    def  list_nodes(self):
        for (node_id, node_address) in self.nodes.items():
            print(f'{node_id:>5} : {node_address}')

    def insert(self, origin_id, key, value):
        node_address = self.nodes[origin_id]
        (host, port) = node_address
        node = rpyc.connect(host, port)
        node.root.insert(key, value)
        node.close()

    def search(self, origin_id, key):
        node_address = self.nodes[origin_id]
        (host, port) = node_address
        node = rpyc.connect(host, port)
        node.root.search(key)
        node.close()

    def exposed_register_node(self, node_id, node_address):
        self.nodes[node_id] = node_address

    def exposed_search_return(self, value):
        if value != None:
            print(f'Chave possui o valor {value}')
        else:
            print('Chave ainda não inserida')

    

if __name__ == "__main__":
    os.setpgrp()
    if len(sys.argv) < 2:
        sys.exit('Necessário passar o parâmetro "n" do anel')
    
    n = int(sys.argv[1])
    ring = NodeRing(n)
    server = ThreadedServer(ring)
    ring.set_address((server.host, server.port))
    
    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    
    print('Inserindo nós...')
    for i in range(ring.max_nodes):
        ring.spawn_node(i)

    while len(ring.nodes) < ring.max_nodes:
        continue
    ring.nodes = {id : ring.nodes[id] for id in sorted(ring.nodes)} 
    print('Nós inseridos!')

    for (node_id, node_address) in ring.nodes.items():
        (host, port) = node_address
        node_finger_table = [{ 'id': (node_id + 2**i) % ring.max_nodes , 'address' : ring.nodes[(node_id + 2**i) % ring.max_nodes]} for i in range(n)]
        node = rpyc.connect(host, port)
        node.root.set_successor(json.dumps(node_finger_table[0]))
        node.root.set_finger_table(json.dumps(node_finger_table))
        node.close()
    
    print('Digite "list" para listar os nós da tabela, "insert" para inserir par chave/valor, "search" para buscar por uma chave e "exit" para sair')
    while True:
        command = input()
        command = command.strip()
        if command == 'list':
            ring.list_nodes()
        elif command == 'insert':
            origin_id = input('ID de origem: ')
            key = input('Chave: ')
            value = input('Valor: ')
            try:
                origin_id = int(origin_id)
                if not key: raise Exception
                if not value: raise Exception
            except:
                print('Erro nos parâmetros da inserção. Tente novamente.')
                continue
            ring.insert(origin_id, key, value)
        elif command == 'search':
            origin_id = input('ID de origem: ')
            key = input('Chave: ')
            try:
                origin_id = int(origin_id)
                if not key: raise Exception
            except:
                print('Erro nos parâmetros da inserção. Tente novamente.')
                continue
            ring.search(origin_id, key)
        elif command == 'exit':
            os.killpg(0, signal.SIGTERM)
        else:
            print('Comando inválido\n')