import socket

HOST = 'localhost'
PORT = 5000

conn = socket.socket()

conn.connect((HOST, PORT))

print('Digite "quit" para sair')
msg = input()
while msg != 'quit' and msg:
    conn.send(msg.encode())
    res = conn.recv(1024)
    print(res.decode())
    msg = input()

conn.close()
