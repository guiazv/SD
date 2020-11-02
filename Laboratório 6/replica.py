import threading
import rpyc
import sys


class Replica(rpyc.Service):

    replicas = {
        1: ('localhost', 5000),
        2: ('localhost', 5001),
        3: ('localhost', 5002),
        4: ('localhost', 5003)
    }

    def __init__(self, id):
        self.id = id
        if id != 1:
            self.is_primary = False
        else:
            self.is_primary = True
        self.x = 0
        self.updates = []
        self.timer = None

    def read(self):
        print(self.x)

    def history(self):
        for (i, update) in enumerate(self.updates, start=1):
            print(f"#{i}: {update}")

    def write(self, value):
        if self.x == value:
            return
        if not self.is_primary:
            success = self.find_primary_and_migrate()
            if not success:
                print(
                    'Não foi possível realizar a migração da cópia primária entre as réplicas')
                return
        self.x = value
        self.updates.append((self.id, value))
        if not self.timer or not self.timer.is_alive():
            self.timer = threading.Timer(15.0, self.propagate)
            self.timer.start()

    def find_primary_and_migrate(self):
        success = False
        for replica_id in [id for id in self.replicas if id != self.id]:
            (host, port) = self.replicas[replica_id]
            replica = rpyc.connect(host, port)
            success = replica.root.give_primary_status(self.id)
            if success:
                self.is_primary = True
                break
        return success

    def propagate(self):
        for replica_id in [id for id in self.replicas if id != self.id]:
            (host, port) = self.replicas[replica_id]
            replica = rpyc.connect(host, port)
            replica.root.update(self.id, self.x)

    def exposed_give_primary_status(self, id):
        if not self.is_primary:
            return False
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
            self.propagate()
        self.is_primary = False
        return True

    def exposed_update(self, primary_id, value):
        self.x = value
        self.updates.append((primary_id, value))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit("Faltando parâmetro do identificador")
    id = int(sys.argv[1])

    replica = Replica(id)
    (host, port) = replica.replicas[id]
    server = rpyc.ThreadedServer(replica, hostname=host, port=port)

    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    print(f'Réplica {replica.id} executando...')

    print("Digite 'read' para ler o valor atual da réplica, 'history' para ver o histórico de alterações na réplica, 'write' para alterar o valor ou 'exit' para sair")
    while True:
        command = input()
        command.strip()
        if command == 'read':
            replica.read()
        elif command == 'history':
            replica.history()
        elif command == 'write':
            value = int(input('Valor a ser escrito: '))
            replica.write(value)
        elif command == 'exit':
            server.close()
            exit()
        else:
            print("Digite 'read' para ler o valor atual da réplica, 'history' para ver o histórico de alterações na réplica, 'write' para alterar o valor ou 'exit' para sair")

