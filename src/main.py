from __future__ import division
import pygame
import sys
import os
import copy
import random

import config
import pygame_game
import screens

def setup_video(fullscreen, create_display):
    pygame.init()
    if create_display:
        if fullscreen:
            pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((1024, 768))
        pygame.display.set_icon(pygame.image.load("gfx/psficon.png").convert_alpha())
        pygame.mouse.set_visible(False)

if __name__ == '__main__':
    # Load config files
    (gc,config_path) = config.get_global_config()

    setup_video(int(gc['fullscreen']) == 1, int(gc['model']) == 0 or int(gc['display_level'])>0)
    if int(gc['display_level']) > 0:
        config.prompt_for_missing_keys(gc,config_path)
        config.prompt_for_simulation_keys(gc)
    config.load_session_and_condition(gc,config_path)
    # Generate seeds for session
    if gc.has_key('session'):
        random.seed(gc['sessions'].index(gc['session'])+hash(gc["id"]))
    else:
        random.seed(hash(gc["id"]))
    seeds = [random.randint(0,10000) for x in xrange(config.get_num_games(gc))]
    # Games
    game_list = config.get_games(gc)
    gstart = config.get_start_game(gc)
    total_bonus = 0
    # model
    model = False
    if int(gc['model']) == 1:
        model = Model(int(gc['model_port']), int(gc['display_level']), gc['model_line_endings'])
        model.wait_for_connection()

    for g in xrange(gstart-1,len(game_list)):
        # Initialize world
        random.seed(seeds[g])
        w = pygame_game.Game(copy.deepcopy(gc),game_list[g],g+1,len(game_list),config_path,model)
        w.log.write_random_seed(seeds[g])
        # Play the game
        #screens.pre_game(w)
        w.game_loop()
        #screens.post_game(w, total_bonus)
        # Clean up
        total_bonus = total_bonus + w.money
        w.log.slog("bonus",{'total':"%d"%total_bonus})
        w.log.close_session_log()
    # End of session
    w.display_bonus(max(0.0, total_bonus))
    sys.exit()
