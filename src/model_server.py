import os
import copy
import config
import threading
import socket
import errno

import model_game
import lisp

class disconnected(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

class Logger(object):
    def __init__(self):
        pass

    def log(self, str):
        print str

class connection (threading.Thread):
    def __init__(self, channel, logger):
        threading.Thread.__init__(self)
        self.channel = channel
        self.log = logger

    def get_next_game (self, gc):
        datapath = config.get_datapath(gc)
        datapath += '/%s/'%gc['id']
        session_name = config.get_session_name(gc)
        if session_name == None:
            session_name = "1"
        i = 0;
        while True:
            game_file = '%s-%s-%d.dat'%(gc['id'], session_name, i)
            incomplete = 'incomplete-' + game_file
            if not (os.path.exists(os.path.join(datapath, game_file)) or os.path.exists(os.path.join(datapath, incomplete))):
                break
            i += 1
        return i

    def send(self, objects):
        #self.log.log ('send %s'%lisp.lispify(objects))
        self.channel.send((lisp.lispify(objects) + self.line_endings).encode('utf-8'));

    def wait_for_continue(self):
        while True:
            #self.log.log("wait for continue")
            buf = self.channel.recv(4096)
            if buf:
                commands = buf.lower().splitlines()
            else:
                raise disconnected('')
            for l in buf.lower().splitlines():
                #self.log.log('line is %s'%l)
                args = l.split(' ')
                if (args[0] == 'continue'):
                    return
                if (args[0] == 'quit'):
                    return

    def do_simple_screen(self, name, delay, objects):
        if delay != None:
            objects['mode'] = 'delay'
            objects['delay_duration'] = delay
            objects['screen-type'] = name
            self.send(objects)
            self.wait_for_continue()
            del objects['delay_duration']
        objects['mode'] = 'events'
        self.send(objects)
        self.wait_for_continue()

    def post_game_screens(self, game, gc, id, gnum):
        self.log.log('%s game %d: total-score'%(id,gnum))
        # for backwards compatibility
        self.do_simple_screen('total-score', 1000, {'total': game.get_total_score(),
                                                    'bonus': game.money,
                                                    'total-bonus': game.money,
                                                    'raw-pnts': game.score.raw_pnts})
        self.log.log('%s game %d: bonus'%(id,gnum))
        self.do_simple_screen('bonus', None, {'bonus': 0})

    def run(self):
        (gc, config_path) = config.get_global_config()
        config.load_session_and_condition(gc, config_path)
        self.line_endings = '\r\n' if gc['model_line_endings'] == 'crlf' else '\n'
        # Fill in missing keys with sane defaults
        if not gc.has_key('id'):
            gc['id'] = 'model'
        game_list = config.get_games(gc)
        gnum = self.get_next_game(gc)
        self.log.log("%s game %d: %s ..."%(gc['id'], gnum, game_list[0]))
        c = config.read_conf(config.get_game_config_file(game_list[0]), copy.deepcopy(gc), config_path, ["#", "\n"])
        g = model_game.ModelGame(c, game_list[0], gnum, self.channel)
        try:
            premature_exit = g.run()
            # Preserve backwards compatibility by presenting a bonus screen
            if premature_exit:
                self.log.log("%s game %d: Premature exit."%(gc['id'], gnum))
            else:
                self.post_game_screens(g, gc, gc['id'], gnum)
            self.channel.close()
            self.log.log("%s game %d: Close connection."%(gc['id'], gnum))
        except disconnected:
            self.log.log("%s game %d: Close connection"%(gc['id'], gnum))
        except socket.error as e:
            if e.errno == errno.ECONNRESET:
                self.log.log("%s game %d: Close connection (reset by peer)"%(gc['id'], gnum))
            else:
                self.log.log("%s game %d: Socket error %d"%(gc['id'], gnum, e.errno))

class Server(object):
    def __init__(self, logger):
        self.log = logger
        self.connections = []

        (gc, config_path) = config.get_global_config()
        port = int(gc['model_port'])

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', port))
        self.socket.listen(10)
        self.log.log("Listening on port %d"%port)

    def handle_connections(self):
        while True:
            channel, details = self.socket.accept()
            channel.setblocking(1)
            self.log.log("New connection ...")
            c = connection(channel, self.log)
            c.setDaemon(True)
            c.start()
            self.connections.append(c)
            self.connections = [ c for c in self.connections if c.is_alive() ]
