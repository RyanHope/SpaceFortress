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
        (self.gc, self.config_path) = config.get_global_config()

        self.setup_video(int(self.gc['fullscreen']) == 1, int(self.gc['model']) == 0 or int(self.gc['display_level'])>0)
        if int(self.gc['display_level']) > 0:
            self.prompt_for_missing_keys()
        self.gc.integrate_session_and_condition()

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
            if self.gc.has_key('conditions'):
                self.gc['condition'] = read_from_list("Choose the condition:", screen, font,self.gc['conditions'])
        if not self.gc.has_key('session'):
            if self.gc.has_key('sessions'):
                try:
                    (resume_session,resume_game) = config.get_resume_info(self.gc, self.config_path)
                except all_sessions_completed:
                    if read_from_list("This subject has completed all sessions!",screen,font,['Pick a session anyway','Quit']) == 1:
                        sys.exit()
                    resume_session = False
                    resume_game = False
                pick_session = True
                if resume_session:
                    idx = self.gc['sessions'].index(resume_session)
                    if idx > 0 or resume_game > 1:
                        pick_session = read_from_list("Resume subject on game %s of session %s?"%(resume_game,resume_session),
                                                      screen,font,['Resume', 'Pick the session'])
                if pick_session:
                    self.gc['session'] = self.gc['sessions'][read_from_list("Choose the session:", screen, font,self.gc['sessions'])]
                else:
                    self.gc['session'] = resume_session
                    self.gc['game'] = resume_game

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
