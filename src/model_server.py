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

    def get_next_game (self):
        datapath = self.gc['datapath']
        datapath += '/%s/'%self.gc['id']
        session_number = self.gc['session']
        if session_number == None:
            session_number = 1
        i = 1;
        while True:
            game_file = '%s-%d-%d.dat'%(self.gc['id'], session_number, i)
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
            objects['condition'] = self.gc['condition']
            objects['session'] = self.gc['session']
            self.channel.send(objects)
            cmd = self.channel.read_command()
            if cmd[0] == 'id' and len(cmd) >= 2:
                self.gc['id'] = cmd[1]
                objects['result'] = True
            if cmd[0] == 'condition' and len(cmd) >= 2:
                if self.gc.raw_config['conditions'].has_key(cmd[0]):
                    self.gc['condition'] = cmd[1]
                    objects['result'] = True
                else:
                    objects['result'] = False
            if cmd[0] == 'session' and len(cmd) >= 2:
                try:
                    s = int(cmd[1])
                    if self.gc.raw_config['sessions'] != None and s >= 1 and s <= len(self.gc.raw_config['sessions']):
                        self.gc['session'] = s
                        objects['result'] = True
                    else:
                        objects['result'] = False
                except ValueError:
                    objects['result'] = False
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

    def fill_in_missing_keys(self):
        if not self.gc.has_key('id'):
            self.gc['id'] = 'model'
        if not self.gc.has_key('condition'):
            if self.gc.raw_config['conditions'] != None:
                lst = sorted(self.gc.raw_config['conditions'].keys())
                self.gc['condition'] = lst[0]
        if not self.gc.has_key('session'):
            if self.gc.raw_config['sessions'] != None:
                self.gc['session'] = 1

    def run(self):
        self.gc = config.get_global_config()
        self.channel = model_socket.ModelSocket(self.raw_channel, '\r\n' if self.gc['model_line_endings'] == 'crlf' else '\n')
        self.fill_in_missing_keys();
        gnum = -1
        self.protocol = int(self.gc['model_interface'])
        try:
            if self.protocol == NEW_PROTOCOL:
                self.do_config_screen()
            self.gc.integrate_session_and_condition()
            game_list = self.gc.get_games()
            gnum = self.get_next_game()
            done = False
            while not done:
                for gname in game_list:
                    self.log.log("%s game %d: %s ..."%(self.gc['id'], gnum, gname))
                    c = self.gc.snapshot(gname)
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

        gc = config.get_global_config()
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
