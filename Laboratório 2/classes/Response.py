import json

class Response:

    def __init__(self, msg: bytes = None):
        if msg != None:
            msg = msg.decode()
            [status, body] = msg.splitlines()
            self.status = status
            self.body = json.loads(body)
    
    def __str__(self):
        return self.status + '\n' + json.dumps(self.body)