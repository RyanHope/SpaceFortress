import pygame
import config
import random

import log
import assets

class Experiment(object):
    def __init__(self):
        self.screens = []
        self.current = None
        self.bonus = 0
        # Load config files
        (self.gc, self.config_path) = config.get_global_config()

        self.setup_video(int(self.gc['fullscreen']) == 1, int(self.gc['model']) == 0 or int(self.gc['display_level'])>0)
        if int(self.gc['display_level']) > 0:
            config.prompt_for_missing_keys(self.gc, self.config_path)
            config.prompt_for_simulation_keys(self.gc)
        config.load_session_and_condition(self.gc, self.config_path)

        # Generate seeds for session
        if self.gc.has_key('session'):
            random.seed(gc['sessions'].index(self.gc['session'])+hash(self.gc["id"]))
        else:
            random.seed(hash(self.gc["id"]))
        self.seeds = [random.randint(0,10000) for x in xrange(config.get_num_games(self.gc))]
        # games
        self.game_list = config.get_games(self.gc)
        self.gstart = config.get_start_game(self.gc)
        self.log = log.session_log(self.gc['id'], config.get_datapath(self.gc), config.get_session_name(self.gc))

    def setup_video(self, fullscreen, create_display):
        pygame.init()
        if create_display:
            if fullscreen:
                pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)
            else:
                pygame.display.set_mode((1024, 768))
            pygame.display.set_icon(pygame.image.load("gfx/psficon.png").convert_alpha())
            pygame.mouse.set_visible(False)
        assets.Assets.load()

    def format_money(self, amount=None):
        if amount == None:
            amount = self.bonus
        return "%d.%02d"%(amount/100,amount%100)

    def jump_to_screen(self,idx):
        self.current = min(max(0, idx), len(self.screens)-1)
        self.screens[self.current].run()

    def next_screen(self):
        self.jump_to_screen(self.current+1)

    def prev_screen(self):
        self.jump_to_screen(self.current-1)

    def run(self):
        self.log.open_slog()
        self.jump_to_screen(0)
        while True:
            self.next_screen()
        self.log.close_slog()
        sys.exit()

# The global experiment object
exp = Experiment()
