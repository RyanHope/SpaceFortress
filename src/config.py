from __future__ import division
import math
import random
import os
import sys
import pygame
import copy
import re
import argparse
from dialog import read_string, read_int, read_from_list

def read_conf(conf_file,config={},config_path='config',ignore=["#", "\n","\r","\t"]):
    configfile = open(os.path.join(config_path, conf_file))
    configlog = configfile.readlines()
    # FIXME: should we make a copy of the base config? I think it doesn't matter at this point. -sabetts
    #config = copy.deepcopy(config)
    for line in configlog:
        if line[0] in ignore:
            pass
        else:
            command = line.split()
            if len(command) > 2:
                config[command[0]] = command[1:]
            else:
                config[command[0]] = command[1]
    configfile.close()
    return config

def get_config_path(config_dir):
    source_location = "../%s/" % config_dir
    app_location = "../../../%s/" % config_dir
    if os.path.exists(source_location):
        return source_location
    elif os.path.exists(app_location):
        return app_location
    else:
        raise Exception("Cannot find config directory: %s"%config_dir)

def get_datapath(gc):
    if gc.has_key('datadir'):
        return gc['datadir']
    elif os.path.exists("../data/"):
        return "../data/"
    elif os.path.exists("../../../data/"):
        return "../../../data/"
    else:
        raise Exception("Cannot find data directory!")

def as_list(gc,key):
    if not isinstance(gc[key], list):
        return [gc[key]]
    else:
        return gc[key]

def get_games (gc):
    if gc.has_key('games'):
        game_list = gc['games']
    elif gc.has_key('n_games'):
        template = gc['n_games']
        num = int(template[0])
        game = template[1]
        game_list = [game]*num
    elif gc.has_key('random_games'):
        random_games = gc['random_games']
        num = int(random_games[0])
        possible = random_games[1:]
        p = map(lambda x: possible[:], range(int(math.ceil(num/len(possible)))))
        map(random.shuffle,p)
        game_list = []
        map(game_list.extend,p)
    else:
        raise Exception("config files must have either games or random_games key.")
    return game_list

def get_game_config_file (game):
    return "config_game_%s.txt"%game

def get_num_games(gc):
    if gc.has_key('games'):
        return len(gc['games'])
    elif gc.has_key('n_games'):
        return int(gc['n_games'][0])
    elif gc.has_key('random_games'):
        return int(gc['random_games'][0])
    else:
        raise Exception("config files must have either games or random_games key.")

def get_condition_name(gc):
    if gc.has_key('conditions'):
        return gc['conditions'][gc['condition']]
    if gc.has_key('condition'):
        return str(gc['condition'])
    else:
        return None

def get_session_name(gc):
    if gc.has_key('sessions'):
        return gc['session']
    if gc.has_key('session'):
        return gc['session']
    else:
        return None

def get_config_files(gc,session=False,condition=False):
    """Return session and condition config files. If sessions or
conditions isn't a key in gc then its assumed that a separate config
file isn't needed. Then None is returned for the corresponding config file."""
    if gc.has_key('sessions'):
        if not session:
            session = gc['session']
    else:
        session = None
    if gc.has_key('conditions'):
        conditions = gc['conditions']
        if not condition:
            condition = conditions[gc['condition']]
    else:
        condition = None
    return ("config_session_%s.txt"%session if session else None,
            "config_condition_%s.txt"%condition if condition else None)

def parse_command_line():
    #When PSF is run as an osx image arg 2 is -psn... so get rid of it.
    args = [a for a in sys.argv[1:] if not re.match('-psn(?:_\d+)+$', a)]
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',help="Specify which directory to load config from",default="config")
    parser.add_argument('--data', metavar="DIR", help="Specify the data directory")
    parser.add_argument('--display-level', metavar="N", help="set the display level (0=no display, 1=minimal, 2=full)",type=int)
    parser.add_argument('--model-port', metavar="PORT", type=int, help="Specify the port to listen on for model clients")
    parser.add_argument('--id', help="Specify the subject ID")
    parser.add_argument('--simulate', help="Play back the key file for a specified game (simulation mode)", action='store_true')
    parser.add_argument('--speedup', metavar="N", help="Specify the simulation speed up factor")
    parser.add_argument('--session', metavar="N", help="Specify the session to simulation")
    parser.add_argument('--game', metavar="N", help="Specify the game to simulation", default="1")
    return parser.parse_args(args)

def get_global_config():
    args = parse_command_line()
    config_dir = args.config
    config_path = get_config_path(config_dir)
    gc = read_conf('config.txt',config_path=config_path)
    # groom config
    if gc.has_key('conditions'):
        if not isinstance(gc['conditions'],list):
            gc['conditions'] = [gc['conditions']]
    if gc.has_key('sessions'):
        if not isinstance(gc['sessions'],list):
            gc['sessions'] = [gc['sessions']]
    if gc.has_key('condition'):
        gc['condition']=int(gc['condition'])
    # add config options from command line
    if args.data != None:
        gc['datadir'] = args.data
    if args.model_port != None:
        gc['model_port'] = args.mode_port
    if args.display_level != None:
        gc['display_level'] = args.display_level
    if args.id != None:
        gc['id'] = args.id
    if args.simulate:
        gc['simulate'] = "1"
        gc['game'] = args.game
        if args.session != None:
            gc['session'] = args.session
        if args.speedup != None:
            gc['speedup'] = args.speedup
    return (gc,config_path)

def get_sessions_and_games(gc,config_path):
    '''Find out how many games are in each session. This is handy when figuring out where to resume.'''
    if gc.has_key('sessions'):
        games = []
        for i in range(len(gc['sessions'])):
            conf = copy.deepcopy(gc)
            load_session_and_condition(conf,config_path,session=gc['sessions'][i])
            games.append(get_num_games(conf))
        return (gc['sessions'],games)
    else:
        return False

def get_next_game(gc,subject_id,session,num_games):
    '''Return the next game to be played in the given session or True if all games have been played.'''
    datapath = get_datapath(gc)
    for g in range(1,num_games+1):
        if not os.path.exists(os.path.join(datapath,'%s-%s-%d.dat'%(subject_id,session,g))):
            return g
    return False

def get_next_session(gc,subject_id,sessions,games):
    '''Return True if the session is complete or the first session that has not been started.'''
    datapath = get_datapath(gc)
    for session,num_games in zip(sessions,games):
        if not os.path.exists(os.path.join(datapath,'%s-%s.dat'%(subject_id,session))) or get_next_game(gc,subject_id,session,num_games):
            return session
    return False

class no_resume_info(Exception):
    def __init__(self,subject_id):
        self.subject_id = subject_id
    def __str__(self):
        "No resume info for subject, %s."%self.subject_id

class all_sessions_completed(Exception):
    def __init__(self,subject_id):
        self.subject_id = subject_id
    def __str__(self):
        "Subject %s has finished all sessions."%self.subject_id
        
def get_resume_info(gc,config_path):
    '''Check the data dir for existing log files to find out what the
    next session and game number are. Returns True when the subject is
    totally finished, None if no resume data can be calculated.'''
    subject_id = gc['id']
    datapath = get_datapath(gc)
    (sessions,games) = get_sessions_and_games(gc,config_path)
    if sessions:
        session = get_next_session(gc,subject_id,sessions,games)
        if session:
            return (session, get_next_game(gc,subject_id,session,games[sessions.index(session)]))
        else:
            raise all_sessions_completed(subject_id)
    else:
            raise no_resume_info(subject_id)

def prompt_for_missing_keys(gc,config_path):
    '''The experiment requires an ID, condition, and session. Prompt
    for them if they don''t exist in the config file.'''
    screen = pygame.display.get_surface()
    font = pygame.font.Font("fonts/freesansbold.ttf", 32)

    if not gc.has_key('id'):
	gc['id'] = read_string("Enter user id:", screen, font)
    if not gc.has_key('condition'):
        if gc.has_key('conditions'):
            gc['condition'] = read_from_list("Choose the condition:", screen, font,gc['conditions'])
    if not gc.has_key('session'):
        if gc.has_key('sessions'):
            try:
                (resume_session,resume_game) = get_resume_info(gc,config_path)
            except all_sessions_completed:
                if read_from_list("This subject has completed all sessions!",screen,font,['Pick a session anyway','Quit']) == 1:
                    sys.exit()
                resume_session = False
                resume_game = False
            pick_session = True
            if resume_session:
                idx = gc['sessions'].index(resume_session)
                if idx > 0 or resume_game > 1:
                    pick_session = read_from_list("Resume subject on game %s of session %s?"%(resume_game,resume_session),
                                                  screen,font,['Resume', 'Pick the session'])
            if pick_session:
                gc['session'] = gc['sessions'][read_from_list("Choose the session:", screen, font,gc['sessions'])]
            else:
                gc['session'] = resume_session
                gc['game'] = resume_game

def prompt_for_simulation_keys(gc):
    '''Simulation mode expects some extra keys to be present. prompt if missing.'''
    if int(gc['simulate']):
        screen = pygame.display.get_surface()
        font = pygame.font.Font("fonts/freesansbold.ttf", 32)
        if gc.has_key('game'):
            gc['game'] = int(gc['game'])
        else:
            gc['game'] = read_int('Enter starting game number: ',screen,font)
        if gc.has_key('speedup'):
            gc['speedup'] = float(gc['speedup'])
        else:
            gc['speedup'] = read_int('Enter speedup value: ',screen,font)

def load_session_and_condition(gc,config_path,session=False,condition=False):
    (session_file, condition_file) = get_config_files(gc,session,condition)
    # since the session and condition don't change from game to game,
    # its safe to load them into the global config
    if condition_file:
        read_conf(condition_file,gc,config_path=config_path)
    if session_file:
        read_conf(session_file,gc,config_path=config_path)
    # Make sure games is a list of games
    if gc.has_key('games'):
        if not isinstance(gc['games'],list):
            gc['games'] = [gc['games']]

def get_start_game(gc):
    if gc.has_key('resume_game'):
        gstart = int(gc['resume_game'])
    elif gc.has_key('game'):
        gstart = int(gc['game'])
    else:
        gstart = 1
    return gstart
