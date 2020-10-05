import socket
import threading
import json


def handle_request(conn, addr):
    while True:
        req = conn.recv(1024)
        req = req.decode()
        if not req:
            break
        else:
            res = process_request(req, conn)
            conn.send(str(res).encode())
    conn.close()


def process_request(req, conn):
    print('\n' + req)
    req = req.split('\n')
    command = req[0]
    if command == 'CONNECT':
        if req[1] in active_users:
            res = 'ERRO\n' + 'Já existe usuário ativo com este nome'
        else:
            lock.acquire()
            active_users[req[1]] = conn
            lock.release()
            res = 'OK'
    elif command == 'DISCONNECT':
        if req[1] in active_users:
            lock.acquire()
            del active_users[req[1]]
            lock.release()
            res = 'OK'
        else:
            res = 'ERRO\n' + 'Este usuário já se desconectou'
    elif command == 'LIST':
        res = 'OK\n' + \
            json.dumps(
                [user for user, skt in active_users.items() if skt != conn])

    elif command == 'MESSAGE':
        to_user = req[1]
        message = req[2]
        if to_user in active_users:
            for user, skt in active_users.items():
                if skt == conn:
                    from_user = user
            if from_user == to_user:
                res = 'ERRO\n' + 'Não é possível enviar mensagens para si mesmo'
            else:
                to_user_socket = active_users[to_user]
                to_user_socket.send(
                    f'MESSAGE\n{from_user}\n{message}'.encode())
                res = 'OK'
        else:
            res = 'ERRO\n' + 'Destinatário não está ativo'
    return res


if __name__ == "__main__":
    HOST = ''
    PORT = 1337

    active_users = {}
    lock = threading.Lock()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen()
    print('Ouvindo na porta {}...'.format(PORT))

    while True:
        conn, addr = sock.accept()
        thread = threading.Thread(target=handle_request, args=(conn, addr))
        thread.start()
    sock.close()
