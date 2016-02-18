import socket
import lisp

class disconnected(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

class ModelSocket(object):
    """Use this class to communicate with the model client."""
    def __init__(self, channel, line_endings):
        super(self.__class__, self).__init__()
        self.channel = channel
        self.line_endings = line_endings
        self.commands = []

    def send(self, objects):
        #self.log.log ('send %s'%lisp.lispify(objects))
        self.channel.send((lisp.lispify(objects) + self.line_endings).encode('utf-8'));

    def read_command(self):
        if len(self.commands) == 0:
            buf = self.channel.recv(4096)
            if buf:
                self.commands = buf.lower().splitlines()
            else:
                raise disconnected('')
        return self.commands.pop(0).split(' ')

    def close(self):
        self.channel.close()
