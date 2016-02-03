from __future__ import division
import pygame
import sys
import drawing
import experiment

from assets import Assets

def format_money(amount):
    return "%d.%02d"%(amount/100,amount%100)

class message(object):
    def __init__(self, name, pause=False, duration=None):
        self.f24 = Assets.f24
        self.f36 = Assets.f36
        self.screen = pygame.display.get_surface()
        self.name = name
        self.pause = pause
        self.duration = duration

    def run(self):
        self.draw()
        self.start()
        if self.pause:
            pygame.time.delay(1000)
        self.handle_events()
        self.end()

    def start(self):
        experiment.exp.log.slog(self.name)

    def end(self):
        experiment.exp.log.slog(self.name + '-end')

    def modifiers(self):
        return (pygame.K_NUMLOCK,
                pygame.K_CAPSLOCK,
                pygame.K_SCROLLOCK,
                pygame.K_RSHIFT,
                pygame.K_LSHIFT,
                pygame.K_RCTRL,
                pygame.K_LCTRL,
                pygame.K_RALT,
                pygame.K_LALT,
                pygame.K_RMETA,
                pygame.K_LMETA,
                pygame.K_LSUPER,
                pygame.K_RSUPER,
                pygame.K_MODE)

    def handle_events(self):
        pygame.event.clear()
        self.start_time = pygame.time.get_ticks()
        while not self.duration or pygame.time.get_ticks() - self.start_time < self.duration:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    elif not event.key in self.modifiers():
                        return
            pygame.time.delay(1)

    def continue_text(self, verb='continue'):
        return drawing.text("Press any key to %s"%verb,self.f24,color=(255,255,0))

class basic_task(message):
    def __init__(self):
        super(self.__class__, self).__init__('basic-task', False)

    def draw(self):
        drawing.fullscreen_message(self.screen, [drawing.text("Your goal is to maximize your points.",self.f36)],
                                   self.continue_text('start'))
        pygame.display.flip()

class instructions(message):
    def __init__(self, text):
        super(self.__class__, self).__init__('instructions', True)
        self.text = text

    def draw(self):
        drawing.fullscreen_message(self.screen,[drawing.text(self.text,self.f36)],
                                   self.continue_text('continue'))
        pygame.display.flip()

class total_score(message):
    def __init__(self, gmax, pause, duration, continue_text, game):
        super(self.__class__, self).__init__('show-total-score', pause, duration)
        self.gmax = gmax
        self.pause = pause
        self.ctext = continue_text
        self.game = game

    def draw(self):
        """shows score for last game and waits to continue"""
        total = self.game.get_total_score()
        self.screen.fill((0, 0, 0))
        if self.game.session_name == None:
            title = "Game %d of %s"%(self.game.game_number, self.gmax)
        else:
            title = "Session %s, Game %d of %s"%(self.sname, self.game.game_number, self.gmax)
        drawing.blit_text(self.screen,self.f24,title,y=100,valign='top',halign='center')
        drawing.blit_text(self.screen,self.f36,"You scored %d points."%self.game.get_total_score(),y=320,valign='top',halign='center')
        drawing.blit_text(self.screen,self.f36,"You earned a bonus of $%s this game."%format_money(self.game.money),y=370,valign='top',halign='center')
        drawing.blit_text(self.screen,self.f36,"So far you have earned a total of $%s."%format_money(experiment.exp.bonus),y=420,valign='top',halign='center')
        self.continue_text(self.ctext).draw(self.screen,700,False)
        pygame.display.flip()

    def start(self):
        score = {'total': self.game.get_total_score(), 'bonus': self.game.money, 'total-bonus': experiment.exp.bonus, 'raw-pnts': self.game.score.raw_pnts}
        experiment.exp.log.slog('show-total-score', score)

    def end(self):
        experiment.exp.log.slog('show-total-score-end')

class score(message):
    def __init__(self,game, pause, continue_text, total_bonus):
        """shows score for last game and waits to continue"""
        super(total_score, self).__init__(pause)
        self.pause = pause
        self.continue_text = continue_text
        self.total_bonus = total_bonus

    def start(self):
        game.log.slog('show-score', score)
        score['screen-type'] = 'score'
        if not game.image and pause:
            game.set_objects(score)
            game.delay(1000)
        game.set_objects(score)
        game.delay_and_log(int(game.config['score_time']))

    def end(self):
        game.log.slog('show-score-end')

    def draw(self):
        total = 0
        score = {}
        self.screen.fill((0, 0, 0))
        if self.game.session_name == None:
            title = "Game %d of %s"%(self.game.game_number, self.game.games_in_session)
        else:
            title = "Session %s, Game %d of %s"%(self.game.session_name, self.game.game_number, self.game.games_in_session)
        drawing.blit_text(self.screen,sel.f24,title,y=100,valign='top',halign='center')
        col1 = []
        col2 = []
        if 'pnts' in self.game.config['active_scores']:
            col1.append(drawing.text("Points",sel.f24, (255, 255,0)))
            col2.append(drawing.text("%d"%self.game.score.pnts,sel.f24))
            total += self.game.score.pnts
            score['pnts'] = self.game.score.pnts
        if 'cntrl' in self.game.config['active_scores']:
            col1.append(drawing.text("CNTRL score:",sel.f24, (255, 255,0)))
            col2.append(drawing.text("%d"%self.game.score.cntrl,sel.f24))
            total += self.game.score.cntrl
            score['cntrl'] = self.game.score.cntrl
        if 'vlcty' in self.game.config['active_scores']:
            col1.append(drawing.text("VLCTY score:",sel.f24, (255, 255,0)))
            col2.append(drawing.text("%d"%self.game.score.vlcty,sel.f24))
            total += self.game.score.vlcty
            score['vlcty'] = self.game.score.vlcty
        if 'speed' in self.game.config['active_scores']:
            col1.append(drawing.text("SPEED score:",sel.f24, (255, 255,0)))
            col2.append(drawing.text("%d"%self.game.score.speed,sel.f24))
            total += self.game.score.speed
            score['speed'] = self.game.score.speed
        if 'crew' in self.game.config['active_scores']:
            crew_score = self.game.score.crew_members * int(self.game.config['crew_member_points'])
            col1.append(drawing.text("Crew Members  x %d"%self.game.score.crew_members,sel.f24, (255, 255,0)))
            col2.append(drawing.text("%d"%crew_score,sel.f24))
            total += crew_score
            score['crew'] = crew_score
        score['total'] = total
        col1.append(drawing.text("Total score for this game",sel.f24,(255, 255,0),padding=20))
        col2.append(drawing.text("%d"%total,sel.f24,padding=20))
        pad = 40
        h = pad+col1[0].rect.h
        y = 200+h*(len(col1)-1)
        drawing.column(self.screen,col1,260,200,align='left',padding=pad)
        drawing.column(self.screen,col2,700,200,align='right',padding=pad)
        pygame.draw.line(self.screen, (255, 255, 255), (210, y), (810, y))
        pygame.draw.rect(self.screen, (255, 255, 255), (210, 200-pad, 601, h*len(col1)+pad), 1)
        col1 = []
        col2 = []
        col1.append(drawing.text("Bonus earned this game", sel.f24, (255, 255, 0)))
        col2.append(drawing.text("$%s"%self.game.format_money(), sel.f24))
        col1.append(drawing.text("Total bonus earned so far", sel.f24, (255, 255, 0)))
        col2.append(drawing.text("$%s"%self.game.format_money(total_bonus+self.game.money), sel.f24))
        score['bonus'] = self.game.money
        score['total-bonus'] = total_bonus+self.game.money
        pad = 20
        h = pad+col1[0].rect.h
        drawing.column(self.screen,col1,260,500,align='left',padding=pad)
        drawing.column(self.screen,col2,700,500,align='right',padding=pad)
        pygame.draw.rect(self.screen, (255, 255, 255), (210, 500-pad, 601, h*len(col1)+pad), 1)

        if continue_text and not self.game.image:
            continue_text.draw(self.screen,700,False)
        pygame.display.flip()

class bonus(message):
    def __init__(self):
        super(bonus, self).__init__(False)

    def draw(self):
        drawing.fullscreen_message(self.screen,[drawing.text("You earned a $%s bonus!"%format_money(experiment.exp.bonus),self.f36,(255,255,0))],
                                   drawing.text("",self.f24))
        pygame.display.flip()

    def handle_events(self):
        pygame.event.clear()
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                sys.exit()

def display_screen(game,screen,continue_text,delay=False,total_bonus=None):
    if screen == 'progress':
        display_progress(game,continue_text)
    elif screen == 'wait-for-caret':
        display_wait(game,)
    elif screen == 'fixation':
        display_fixation(game,)
    elif screen == 'instructions':
        display_instructions(game,continue_text)
    elif screen == 'foe-mines':
        display_foe_mines(game,continue_text)
    elif screen == 'fmri-task':
        display_fmri_task(game,continue_text)
    elif screen == 'incremental-task':
        display_inc_task(game,continue_text)
    elif screen == 'basic-task':
        display_basic_task(game,continue_text)
    elif screen == 'transfer-task':
        display_transfer_task(game,continue_text)
    elif screen == 'score':
        show_score(game,delay, continue_text, total_bonus)
    elif screen == 'total-score':
        show_total_score(game,delay,continue_text, total_bonus)
    elif screen == 'fixation':
        display_fixation(game,)
    elif screen != 'none':
        display_screen_from_file(game,screen)

def pre_game_continue_text(game,last):
    if last:
        return continue_text("begin")
    else:
        return continue_text("continue")

def display_pre_game_screens(game):
    for n in xrange(len(game.pre_game_screens)):
        screen = game.pre_game_screens[n]
        last = n == len(game.pre_game_screens)-1
        continue_text = game.pre_game_continue_text(last)
        display_screen(game, screen, continue_text)

def post_game_continue_text(game,last,end):
    if game.image:
        return None
    elif end:
        if game.has_display():
            return drawing.text("You're done! Press any key to exit",game.f24,(0,255,0))
    elif last:
        return continue_text('continue to next game')
    else:
        return continue_text('continue')

def display_post_game_screens(game, total_bonus):
    end = game.game_number == game.games_in_session
    for n in xrange(len(game.post_game_screens)):
        screen = game.post_game_screens[n]
        delay = n == 0
        last = n == len(game.post_game_screens)-1
        continue_text = game.post_game_continue_text(last,end)
        game.display_screen(screen,continue_text,delay,total_bonus)

def display_block_start_screens(game):
    for screen in game.block_start_screens:
        game.display_screen(screen,continue_text('continue'))

def display_block_end_screens(game):
    for screen in game.block_end_screens:
        game.display_screen(screen,continue_text('continue'))

def display_session_screens(game):
    for screen in game.session_start_screens:
        display_screen(screen,continue_text('continue'))

def pre_game(game):
    if not game.simulate:
        # pre game screens
        if game.game_number == 1:
            display_session_screens(game)
        if game.games_per_block > 0 and game.game_number % game.games_per_block == 1:
            display_block_start_screens(game)
            game.log.slog('block-start',{'block':game.game_number//game.games_per_block+1})
        display_pre_game_screens(game)

def post_game(game, total_bonus):
    '''Call this once the game is done.'''
    if game.sounds_enabled:
        pygame.mixer.stop()
    # display screens
    if not game.simulate:
        display_post_game_screens(game, total_bonus)
        if game.games_per_block > 0 and game.game_number % game.games_per_block == 0:
            game.log.slog('block-end',{'block':game.game_number//game.games_per_block})
            game.display_block_end_screens()
