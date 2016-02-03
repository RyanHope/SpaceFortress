import os
import copy
import config
import threading
import socket

import model_game
import lisp

class connection (threading.Thread):
    def __init__(self, channel):
        threading.Thread.__init__(self)
        self.channel = channel

    def get_next_game (self, gc):
        datapath = config.get_datapath(gc)
        datapath += '/%s/'%gc['id']
        session_name = config.get_session_name(gc)
        if session_name == None:
            session_name = "1"
        i = 0;
        while True:
            game_file = '%s-%s-%d.dat'%(gc['id'], session_name, i)
            if not os.path.exists(os.path.join(datapath, game_file)):
                break
            i += 1
        return i

    def bonus_screen(self, gc):
        print 'bonus'
        line_endings = '\r\n' if gc['model_line_endings'] == 'crlf' else '\n'
        self.channel.send((lisp.lispify({'screen-type': 'bonus', 'bonus': 0}) + line_endings).encode('utf-8'));
        self.channel.recv(4096)

    def run(self):
        (gc, config_path) = config.get_global_config()
        config.load_session_and_condition(gc, config_path)
        # Fill in missing keys with sane defaults
        if not gc.has_key('id'):
            gc['id'] = 'model'
        game_list = config.get_games(gc)
        gnum = self.get_next_game(gc)
        print "Model game %d: %s ..."%(gnum, game_list[0])
        c = config.read_conf(config.get_game_config_file(game_list[0]), copy.deepcopy(gc), config_path, ["#", "\n"])
        g = model_game.ModelGame(c, game_list[0], gnum, self.channel)
        premature_exit = g.run()
        # Preserve backwards compatibility by presenting a bonus screen
        if not premature_exit:
            self.bonus_screen(gc)
        self.channel.close()
        print "Close connection ..."

class Server(object):
    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('',port))
        self.socket.listen(10)
        print "Listening on port", port

    def handle_connections(self):
        while True:
            channel, details = self.socket.accept()
            channel.setblocking(1)
            print "New connection ..."
            c = connection(channel)
            c.start()

if __name__ == '__main__':
    (gc, config_path) = config.get_global_config()
    config.load_session_and_condition(gc, config_path)
    game_list = config.get_games(gc)
    # gstart = int(config.get_start_game(gc))

    s = Server(int(gc['model_port']))
    s.handle_connections()
