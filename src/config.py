from __future__ import division
import math
import random
import os
import sys
import copy
import re
import argparse
import yaml

class Config(object):
    def __init__(self, config_file):
        super(self.__class__, self).__init__()
        self.file = config_file
        with open(self.file) as stream:
            self.raw_config = yaml.load(stream)
        self.global_config = self.raw_config['global']
        self.groom()

    def groom(self):
        if not self.global_config.has_key('datapath'):
            if os.path.exists("../data/"):
                self.global_config['datapath'] = "../data/"
            elif os.path.exists("../../../data/"):
                self.global_config['datapath'] = "../../../data/"
            else:
                raise Exception("Cannot find data directory!")
        if not self.global_config.has_key('condition'):
            if self.raw_config['conditions'] == None:
                self.global_config['condition'] = None
            elif len(self.raw_config['conditions']) == 1:
                self.global_config['condition'] = self.raw_config['conditions'].keys()[0]
        if not self.global_config.has_key('session'):
            if self.raw_config['sessions'] == None:
                self.global_config['session'] = None
            elif len(self.raw_config['sessions']) == 1:
                self.global_config['session'] = 1

    def integrate_session_and_condition(self):
        # since the session and condition don't change from game to game,
        # its safe to load them into the global config
        if self.raw_config['conditions'] != None and len(self.raw_config['conditions'])>0:
            for k,v in self.raw_config['conditions'][self.global_config['condition']].iteritems():
                self.global_config[k] = v
        if self.raw_config['sessions'] != None and len(self.raw_config['sessions'])>0:
            for k,v in self.raw_config['sessions'][self.global_config['session']-1].iteritems():
                self.global_config[k] = v

    def get_games (self):
        if self.global_config.has_key('games'):
            game_list = self.global_config['games']
        elif self.global_config.has_key('n_games'):
            template = self.global_config['n_games']
            num = int(template[0])
            game = template[1]
            game_list = [game]*num
        elif self.global_config.has_key('random_games'):
            random_games = self.global_config['random_games']
            num = int(random_games[0])
            possible = random_games[1:]
            p = map(lambda x: possible[:], range(int(math.ceil(num/len(possible)))))
            map(random.shuffle,p)
            game_list = []
            map(game_list.extend,p)
        else:
            raise Exception("config files must have either games, n_games, or random_games key.")
        return game_list

    def get_num_games(self):
        if self.global_config.has_key('games'):
            return len(self.global_config['games'])
        elif self.global_config.has_key('n_games'):
            return int(self.global_config['n_games'][0])
        elif self.global_config.has_key('random_games'):
            return int(self.global_config['random_games'][0])
        else:
            raise Exception("config files must have either games, n_games, or random_games key.")

    def get_start_game(self):
        if self.global_config.has_key('resume_game'):
            gstart = int(self.global_config['resume_game'])
        elif self.global_config.has_key('game'):
            gstart = int(self.global_config['game'])
        else:
            gstart = 1
        return gstart

    def snapshot(self, game):
        """Create a dictionary containing keys from the global, condition, sesession, and game configs."""
        config = copy.deepcopy(self.global_config)
        if game:
            for k,v in self.raw_config['games'][game].iteritems():
                config[k] = v
        return config

    def __getitem__(self, key):
        return self.global_config[key]

    def __setitem__(self, key, value):
        self.global_config[key] = value

    def __contains__(self, key):
        return self.global_config.has_key(key)

    def has_key(self, key):
        return self.__contains__(key)

def get_config_path(config_dir):
    source_location = "../%s/" % config_dir
    app_location = "../../../%s/" % config_dir
    if os.path.exists(source_location):
        return source_location
    elif os.path.exists(app_location):
        return app_location
    else:
        raise Exception("Cannot find config directory: %s"%config_dir)

def as_list(gc,key):
    if not isinstance(gc[key], list):
        return [gc[key]]
    else:
        return gc[key]

def parse_command_line():
    #When PSF is run as an osx image arg 2 is -psn... so get rid of it.
    args = [a for a in sys.argv[1:] if not re.match('-psn(?:_\d+)+$', a)]
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-dir',help="Specify where the config files are located",default="config")
    parser.add_argument('--config',help="Specify which config file to load config from",default="space-fortress")
    parser.add_argument('--data', metavar="DIR", help="Specify the data directory")
    parser.add_argument('--debug', help="Turn on debug keys bindings", action='store_true')
    parser.add_argument('--display-level', metavar="N", help="set the display level (0=no display, 1=minimal, 2=full)",type=int)
    parser.add_argument('--model-port', metavar="PORT", type=int, help="Specify the port to listen on for model clients")
    parser.add_argument('--id', help="Specify the subject ID")
    parser.add_argument('--session', metavar="N", help="Specify the session")
    parser.add_argument('--condition', metavar="N", help="Specify the condition")
    parser.add_argument('--game', metavar="N", help="Specify the game (used in simulation mode)")
    return parser.parse_args(args)

def get_global_config():
    args = parse_command_line()
    config_dir = args.config_dir
    config_path = get_config_path(config_dir)
    gc = Config(os.path.join(config_path, '%s.yml'%args.config))
    # add config options from command line
    if args.data != None:
        gc['datapath'] = args.data
    if args.model_port != None:
        gc['model_port'] = args.mode_port
    if args.display_level != None:
        gc['display_level'] = args.display_level
    if args.id != None:
        gc['id'] = args.id
    if args.session != None:
        gc['session'] = args.session
    if args.condition != None:
        gc['condition'] = args.condition
    if args.game:
        gc['game'] = args.game
    if args.debug:
        gc['debug'] = 1
    return gc
