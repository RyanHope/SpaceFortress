import os
import copy
import config
import difflib

import sim_game

def diff(game):
    orig_game = os.path.join(game.log.datapath,"%s-%s-%d.dat"%(game.log.id, game.log.session, game.log.game))
    sim_game = os.path.join(game.log.datapath,"%s-%s-%d.sim.dat"%(game.log.id, game.log.session, game.log.game))
    orig_lines = open(orig_game, 'U').readlines()
    sim_lines = open(sim_game, 'U').readlines()
    sm = difflib.SequenceMatcher(None, orig_lines, sim_lines)
    r = sm.ratio()
    if r != 1.0:
        print('Differences! %f'%r)


if __name__ == '__main__':
    gc = config.get_global_config()
    gc.integrate_session_and_condition()
    game_list = gc.get_games()
    # gstart = int(config.get_start_game(gc))
    for i in xrange(len(game_list)):
        print "Simulating game %d ..."%(i+1)
        c = gc.snapshot(games_list[i])
        g = sim_game.SimGame(c, game_list[i], i+1)
        g.run()
        diff(g)
