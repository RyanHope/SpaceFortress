from __future__ import division
import pygame
import sys
import drawing
import screen
from experiment import exp
from assets import Assets

from contrib import gui

def format_money(amount):
    return "%d.%02d"%(amount/100,amount%100)

class message(screen.Screen):
    def __init__(self, screen_name, pause=False, duration=None):
        screen.Screen.__init__(self, screen_name)
        # super(self.__class__, self).__init__(screen_name)
        self.f24 = Assets.f24
        self.f36 = Assets.f36
        self.screen = pygame.display.get_surface()
        self.pause = pause
        self.duration = duration

    def run(self):
        self.draw()
        self.start()
        if self.pause:
            exp.delay_and_handle_events(1000)
        self.handle_events()
        self.end()

    def start(self):
        exp.slog('start')

    def end(self):
        exp.slog('end')

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
                if exp.handle_event(event):
                    pass
                elif event.type == pygame.KEYDOWN:
                    if not event.key in self.modifiers():
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
        super(self.__class__, self).__init__('total-score', pause, duration)
        self.gmax = gmax
        self.ctext = continue_text
        self.game = game

    def draw(self):
        """shows score for last game and waits to continue"""
        total = self.game.get_total_score()
        self.screen.fill((0, 0, 0))
        if self.game.session_number == None:
            title = "Game %d of %s"%(self.game.game_number, self.gmax)
        else:
            title = "Session %d, Game %d of %s"%(self.game.session_number, self.game.game_number, self.gmax)
        drawing.blit_text(self.screen,self.f24,title,y=100,valign='top',halign='center')
        drawing.blit_text(self.screen,self.f36,"You scored %d points."%self.game.get_total_score(),y=320,valign='top',halign='center')
        drawing.blit_text(self.screen,self.f36,"You earned a bonus of $%s this game."%format_money(self.game.money),y=370,valign='top',halign='center')
        drawing.blit_text(self.screen,self.f36,"So far you have earned a total of $%s."%format_money(exp.bonus),y=420,valign='top',halign='center')
        self.continue_text(self.ctext).draw(self.screen,700,False)
        pygame.display.flip()

    def start(self):
        score = {'game-number': self.game.game_number, 'total': self.game.get_total_score(), 'bonus': self.game.money, 'total-bonus': exp.bonus, 'raw-pnts': self.game.score.raw_pnts}
        exp.slog('start', score)

    def end(self):
        exp.slog('end')

class score(message):
    def __init__(self, gmax, pause, duration, continue_text, game):
        """shows score for last game and waits to continue"""
        super(total_score, self).__init__(gmax, pause, duration, continue_text, game)

    def start(self):
        score = {'total': self.game.get_total_score(), 'bonus': self.game.money, 'total-bonus': exp.bonus, 'raw-pnts': self.game.score.raw_pnts}
        exp.slog('start', score)

    def end(self):
        exp.slog('end')

    def draw(self):
        total = 0
        score = {}
        self.screen.fill((0, 0, 0))
        if self.game.session_number == None:
            title = "Game %d of %s"%(self.game.game_number, self.game.games_in_session)
        else:
            title = "Session %d, Game %d of %s"%(self.game.session_number, self.game.game_number, self.game.games_in_session)
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
        super(bonus, self).__init__('bonus', False)

    def start(self):
        obj = {'bonus': exp.bonus}
        exp.slog('start', obj)

    def draw(self):
        drawing.fullscreen_message(self.screen,[drawing.text("You earned a $%s bonus!"%format_money(exp.bonus),self.f36,(255,255,0))],
                                   drawing.text("",self.f24))
        pygame.display.flip()

    def handle_events(self):
        pygame.event.clear()
        while True:
            event = pygame.event.wait()
            if exp.handle_event(event):
                pass
            elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return

class textarea(gui.TextArea):
    def event(self,e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_TAB:
            if (e.mod&pygame.KMOD_SHIFT) == 0:
                self.next()
            else:
                self.previous()
            return True
        return gui.TextArea.event(self, e)

class questionnaire_desktop(gui.Desktop):
    def event(self, ev):
        if exp.handle_event(ev):
            return True
        else:
            return gui.Desktop.event(self, ev)

class questionnaire(screen.Screen):
    def __init__(self):
        screen.Screen.__init__(self, 'questionnaire')
        self.screen = pygame.display.get_surface()

    def click_continue(self):
        self.done = True

    def quit(self):
        sys.exit()

    def add_question(self, c, query):
        ta = textarea(width=450, height=100)
        c.tr()
        c.td(gui.Label(query, font=Assets.f24))
        c.tr()
        c.td(ta,border=3, style={'padding_bottom': 20})
        return ta

    def draw(self):
        self.app.repaint()

    def run(self):
        exp.slog('start')
        pygame.mouse.set_visible(True)
        self.done = False
        self.app = questionnaire_desktop(theme=gui.Theme('gui-theme'))
        c = gui.Table(padding=20)
        c.tr()
        c.td(gui.Label('Please Answer the Following Questions',
                       font=Assets.f36,
                       color=(255,255,0)),
             align=-1, style={"padding_bottom": 20})
        strategy = self.add_question(c, "What is your overall strategy?")
        thrust = self.add_question(c, "How do you decide when to thrust?")
        turn = self.add_question(c, "How do you decide when to turn?")
        shoot = self.add_question(c, "How do you decide when to shoot?")

        cont = gui.Button("Continue")
        cont.connect(gui.CLICK, self.click_continue)
        c.tr()
        c.td(cont)

        strategy.focus()

        self.app.init(c, None)
        while not self.done:
            self.app.loop()
            pygame.time.wait(5)

        exp.slog('end', {'strategy': str(strategy.value),
                         'thrust': str(thrust.value),
                         'turn': str(turn.value),
                         'shoot': str(shoot.value)})

        pygame.mouse.set_visible(False)
