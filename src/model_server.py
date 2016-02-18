import os
import copy
import config
import threading
import socket
import errno

import model_socket
import model_game

OLD_PROTOCOL = 1
NEW_PROTOCOL = 2

class Logger(object):
    def __init__(self):
        pass

    def log(self, str):
        print str

class connection (threading.Thread):
    def __init__(self, channel, logger):
        threading.Thread.__init__(self)
        self.raw_channel = channel
        self.log = logger

    def get_next_game (self, gc):
        datapath = config.get_datapath(gc)
        datapath += '/%s/'%gc['id']
        session_name = config.get_session_name(gc)
        if session_name == None:
            session_name = "1"
        i = 1;
        while True:
            game_file = '%s-%s-%d.dat'%(gc['id'], session_name, i)
            incomplete = 'incomplete-' + game_file
            if not (os.path.exists(os.path.join(datapath, game_file)) or os.path.exists(os.path.join(datapath, incomplete))):
                break
            i += 1
        return i

    def wait_for_continue(self):
        while True:
            cmd = self.channel.read_command()
            if cmd[0] in ['continue', 'quit']:
                break

    def do_simple_screen(self, name, delay, objects):
        if delay != None:
            objects['mode'] = 'delay'
            objects['delay_duration'] = delay
            objects['screen-type'] = name
            self.channel.send(objects)
            self.wait_for_continue()
            del objects['delay_duration']
        objects['mode'] = 'events'
        self.channel.send(objects)
        self.wait_for_continue()

    def post_game_screens(self, game, gc, id, gnum):
        self.log.log('%s game %d: score'%(id,gnum))
        objects = {'total': game.get_total_score(),
                   'bonus': game.money,
                   'total-bonus': game.money,
                   'raw-pnts': game.score.raw_pnts}
        if self.protocol == NEW_PROTOCOL:
            self.do_simple_screen('score', 0, objects)
        elif self.protocol == OLD_PROTOCOL:
            self.do_simple_screen('total-score', 1000, objects)
        else:
            raise Exception ("Unknown protocol version")

    def do_config_screen (self):
        objects = {}
        objects['screen-type'] = 'config'
        objects['mode'] = 'config'

        while True:
            objects['id'] = self.gc['id']
            self.channel.send(objects)
            cmd = self.channel.read_command()
            if cmd[0] == 'id' and len(cmd) >= 2:
                self.gc['id'] = cmd[1]
                objects['result'] = True
            elif cmd[0] == 'config' and len(cmd) >= 3:
                if len(cmd) > 3:
                    self.gc[cmd[1]] = cmd[2:]
                else:
                    self.gc[cmd[1]] = cmd[2]
                objects['result'] = True
            elif cmd[0] == 'continue':
                return
            else:
                objects['result'] = False

    def run(self):
        (self.gc, config_path) = config.get_global_config()
        self.channel = model_socket.ModelSocket(self.raw_channel, '\r\n' if self.gc['model_line_endings'] == 'crlf' else '\n')
        config.load_session_and_condition(self.gc, config_path)
        if not self.gc.has_key('id'):
            self.gc['id'] = 'model'
        gnum = -1
        self.protocol = int(self.gc['model_interface'])
        try:
            if self.protocol == NEW_PROTOCOL:
                self.do_config_screen()
            game_list = config.get_games(self.gc)
            gnum = self.get_next_game(self.gc)
            done = False
            while not done:
                for gname in game_list:
                    self.log.log("%s game %d: %s ..."%(self.gc['id'], gnum, gname))
                    c = config.read_conf(config.get_game_config_file(gname), copy.deepcopy(self.gc), config_path, ["#", "\n"])
                    g = model_game.ModelGame(c, gname, gnum, self.channel)
                    done = g.run()
                    if done:
                        self.log.log("%s game %d: Premature exit."%(self.gc['id'], gnum))
                        break
                    else:
                        self.post_game_screens(g, self.gc, self.gc['id'], gnum)
                    gnum += 1
            self.channel.close()
            self.log.log("%s game %d: Close connection."%(self.gc['id'], gnum))
        except model_socket.disconnected:
            self.log.log("%s game %d: Disconnected"%(self.gc['id'], gnum))
        except socket.error as e:
            if e.errno == errno.ECONNRESET:
                self.log.log("%s game %d: Close connection (reset by peer)"%(self.gc['id'], gnum))
            else:
                self.log.log("%s game %d: Socket error %d"%(self.gc['id'], gnum, e.errno))

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
