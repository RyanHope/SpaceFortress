from __future__ import division
import sys
import os
import copy
import random

import config
import sdl_game
import screens
from experiment import exp

def get_screen(name, game):
    # print name
    if name == 'instructions':
        return screens.instructions("Ask Experimenter for Instructions")
    elif name == 'basic-task':
        return screens.basic_task()
    elif name == 'total-score':
        return screens.total_score(len(exp.game_list), True, int(game.config['score_time']), 'continue', game)
    else:
        raise Exception('unknown screen "%s"'%name)

def gen_screens():
    for s in config.as_list(exp.gc,'session_start_screens'):
        exp.screens.append(get_screen(s, None))
    gnum = 0
    for g in exp.game_list:
        c = exp.gc.snapshot(g)
        game = sdl_game.SDLGame(c, g, gnum+1)
        for s in config.as_list(exp.gc,'pre_game_screens'):
            exp.screens.append(get_screen(s, game))
        exp.screens.append(game)
        # print g
        for s in config.as_list(exp.gc,'post_game_screens'):
            exp.screens.append(get_screen(s, game))
        gnum += 1
    exp.screens.append(screens.bonus())

def start_sdl_experiment():
    exp.setup()
    gen_screens()
    exp.run()

if __name__ == '__main__':
    start_sdl_experiment()
