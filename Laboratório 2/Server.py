from Response import Response
import socket
import re
from collections import defaultdict

class Server:
    
    host = ''
    port = 5000

    def __init__(self):
        self.__skt = socket.socket()
    
    def listen(self, host = host, port = port):
        self.__skt.bind((Server.host, port))
        self.__skt.listen(1)
        print('Ouvindo na porta {}...'.format(port))
        while True:
            conn, addr = self.__skt.accept()
            while True:
                req = conn.recv(1024)
                req = req.decode()
                if not req:
                    conn.close()
                    break
                else:
                    res = self.__process_request(req)
                    conn.send(str(res).encode())
            
        self.__skt.close()

    
    def __count_words(self, file):

        file = file.lower()
        word_list = re.findall(r'\b\w+\b', file)
        word_frequency = defaultdict(int)
        for word in word_list:
            word_frequency[word] += 1

        top_words = sorted(word_frequency.items(), key=lambda d: d[1], reverse=True)[:10]
        res = {}
        for (w,f) in top_words:
            res[w] = f
        return res

    def __process_request(self, path):
        response = Response()
        try:
            file = open(path)
        except OSError:
            response.status = 'ERROR'
            response.body = 'Arquivo não pode ser aberto'
            return response
        
        file_content = file.read()
        body = self.__count_words(file_content)
        response.status = 'OK'
        response.body = body
        return response


