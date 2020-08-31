import socket

HOST = ''
PORT = 5000

skt = socket.socket()
skt.bind((HOST, PORT))
skt.listen(1)

while True:
    conn, addr = skt.accept()
    print('Conectado com ' + str(addr))
    while True:
        msg = conn.recv(1024)
        if not msg:
            conn.close()
            break
        else:
            conn.send(msg)
        
skt.close()
    
