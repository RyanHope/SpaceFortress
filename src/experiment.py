import pygame
import config
import random
from sfdialog import read_string, read_int, read_from_list

import log
import assets
import sounds

class Experiment(object):
    def __init__(self):
        self.screens = []
        self.current = None
        self.bonus = 0

    def setup(self):
        # Load config files
        self.gc = config.get_global_config()

        self.setup_video(int(self.gc['fullscreen']) == 1, int(self.gc['model']) == 0 or int(self.gc['display_level'])>0)
        if int(self.gc['display_level']) > 0:
            self.prompt_for_missing_keys()
        self.gc.integrate_session_and_condition()
        # Generate seeds for session
        if self.gc['session'] != None:
            random.seed(hash(self.gc['session']) + hash(self.gc["id"]))
        else:
            random.seed(hash(self.gc["id"]))
        self.seeds = [random.randint(0,10000) for x in xrange(self.gc.get_num_games())]
        # games
        self.log = log.session_log(self.gc['id'], self.gc['datapath'], self.gc['session'])

    def setup_video(self, fullscreen, create_display):
        pygame.mixer.pre_init(frequency=44100, buffer=2048)
        pygame.init()
        if create_display:
            if fullscreen:
                pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)
            else:
                pygame.display.set_mode((1024, 768))
            pygame.display.set_icon(pygame.image.load("gfx/psficon.png").convert_alpha())
            pygame.mouse.set_visible(False)
        assets.Assets.load()
        sounds.Sounds.load()

    def prompt_for_missing_keys(self):
        '''The experiment requires an ID, condition, and session. Prompt
        for them if they don''t exist in the config file.'''
        screen = pygame.display.get_surface()
        font = pygame.font.Font("fonts/freesansbold.ttf", 32)

        if not self.gc.has_key('id'):
            self.gc['id'] = read_string("Enter user id:", screen, font)
        if not self.gc.has_key('condition'):
            if self.gc.raw_config['conditions'] != None:
                lst = sorted(self.gc.raw_config['conditions'].keys())
                self.gc['condition'] = lst[read_from_list("Choose the condition:", screen, font, lst)]
        if not self.gc.has_key('session'):
            if self.gc.raw_config['sessions'] != None:
                self.gc['session'] = read_from_list("Choose the session:", screen, font, [ i+1 for i in self.gc.raw_config['sessions'] ])

    # def prompt_for_simulation_keys(gc):
    #     '''Simulation mode expects some extra keys to be present. prompt if missing.'''
    #     if int(gc['simulate']):
    #         screen = pygame.display.get_surface()
    #         font = pygame.font.Font("fonts/freesansbold.ttf", 32)
    #         if gc.has_key('game'):
    #             gc['game'] = int(gc['game'])
    #         else:
    #             gc['game'] = read_int('Enter starting game number: ',screen,font)
    #         if gc.has_key('speedup'):
    #             gc['speedup'] = float(gc['speedup'])
    #         else:
    #             gc['speedup'] = read_int('Enter speedup value: ',screen,font)

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
