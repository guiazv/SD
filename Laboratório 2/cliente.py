from Response import Response
import socket

HOST = 'localhost'
PORT = 5000

conn = socket.socket()

conn.connect((HOST, PORT))

msg = input('Digite o caminho para o arquivo: ')
while msg:
    conn.send(msg.encode())
    res = conn.recv(1024)
    response = Response(res)
    if response.status == 'ERROR':
        print(response.body)
    else:
        print(str(response))
        for word in response.body:
            print(word + ' ' + str(response.body[word]))
        
    msg = input('Digite o caminho para o arquivo: ')

conn.close()