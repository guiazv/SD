from classes.Response import Response
import socket
import re
import select
import sys
import multiprocessing
from collections import defaultdict

class Server:
    
    host = ''
    port = 5000

    def __init__(self):
        self.__skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__skt.setblocking(False)
        self.__fds = [self.__skt, sys.stdin]
        self.__connections = {}
        self.__processes = []
    
    def listen(self, host = host, port = port):
        self.__skt.bind((Server.host, port))
        self.__skt.listen(1)
        print('Ouvindo na porta {}...'.format(port))
        while True:
            r, w, e = select.select(self.__fds, [], [])

            for fd in r:
                if fd == self.__skt:
                    conn, addr = self.__skt.accept()
                    self.__connections[addr] = conn
                    process = multiprocessing.Process(target=self.__handle_requests, args=(conn, addr))
                    process.start()
                    self.__processes.append(process)
                elif fd == sys.stdin:
                    cmd = input()
                    if cmd == 'exit':
                        for process in self.__processes:
                            process.join()
                        self.__skt.close()
                        sys.exit()


        

    def __handle_requests(self, conn, addr):
        while True:
            req = conn.recv(1024)
            req = req.decode()
            if not req:
                break
            else:
                res = self.__process_request(req)
                conn.send(str(res).encode())
        conn.close()

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


