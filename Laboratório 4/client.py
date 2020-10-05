import socket
import json
import select
import sys


def connect(conn, username):
    if not username:
        return False
    else:
        req = 'CONNECT\n' + username
        conn.send(req.encode())
        res = conn.recv(1024)
        res = res.decode().split('\n')
        if res[0] == 'OK':
            print('Conectado!')
            return True
        elif res[0] == 'ERRO':
            print(res[1])
            return False


def disconnect(conn):
    req = 'DISCONNECT\n' + username
    conn.send(req.encode())
    res = conn.recv(1024)
    conn.close()
    exit()


def list_users(conn):
    msg = 'LIST'
    conn.send(msg.encode())
    res = conn.recv(1024)
    res = res.decode().split('\n')
    active_users = json.loads(res[1])
    print('=================================')
    if len(active_users) == 0:
        print('Não há usuários ativos no momento')
    for index in range(len(active_users)):
        print(active_users[index])
        if index != len(active_users) - 1:
            print('---------------------------------')
    print('=================================')


if __name__ == "__main__":

    HOST = 'localhost'
    PORT = 1337

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    conn.connect((HOST, PORT))
    fds = [sys.stdin, conn]

    username = input('Qual o seu nome de usuário?\n')
    connected = connect(conn, username)
    while not connected:
        username = input('Qual o seu nome de usuário?\n')
        connected = connect(conn, username)

    print('Digite "list" para listar os usuários ativos ou "exit" para sair')
    print('Para enviar uma mensagem: nomedousuario < mensagem')
    while True:
        r, w, e = select.select(fds, [], [])
        for fd in r:
            if fd == conn:
                res = conn.recv(1024).decode().split('\n')
                if res[0] == 'MESSAGE':
                    from_user = res[1]
                    content = res[2]
                    print(from_user + ' > ' + content)
                elif res[0] == 'ERRO':
                    print(res[1])
            elif fd == sys.stdin:
                command = input()
                if not command:
                    continue
                elif command == 'exit':
                    disconnect(conn)
                elif command == 'list':
                    list_users(conn)
                else:
                    message = command.split('<', 1)
                    if len(message) < 2:
                        print('Para enviar uma mensagem: nomedousuario < mensagem')
                        continue
                    [user, content] = message
                    user = user.strip()
                    content = content.strip()
                    req = f'MESSAGE\n{user}\n{content}'
                    conn.send(req.encode())
