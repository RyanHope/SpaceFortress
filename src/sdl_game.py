from __future__ import division
import pygame
import os
import sys
import time
import sounds
import game
import log
import config
import missile
from experiment import exp
from assets import Assets

import pygame_objects as pyobj

class SDLGame(game.Game):
    def __init__(self, conf, game_name, game_number):
        super(self.__class__, self).__init__(conf, game_name, game_number, None)
        # input
        self.key_bindings = {eval("pygame.K_%s"%self.config["thrust_key"]): 'thrust',
                             eval("pygame.K_%s"%self.config["left_turn_key"]): 'left',
                             eval("pygame.K_%s"%self.config["right_turn_key"]): 'right',
                             eval("pygame.K_%s"%self.config["fire_key"]): 'fire',
                             eval("pygame.K_%s"%self.config["IFF_key"]): 'iff',
                             eval("pygame.K_%s"%self.config["shots_key"]): 'shots',
                             eval("pygame.K_%s"%self.config["pnts_key"]): 'pnts'}

        # self.keys_pressed = {self.thrust_key:False, self.left_turn_key:False,
        #                      self.right_turn_key:False, self.fire_key:False,
        #                      self.IFF_key:False, self.shots_key:False,
        #                      self.pnts_key:False}
        # audio
        self.sounds_enabled = int(self.config['sounds']) == 1
        # graphics
        self.load_display_assets()
        r = self.screen.get_rect()

        self.SCREEN_WIDTH = r.width
        self.SCREEN_HEIGHT = r.height
        self.worldsurf = pygame.Surface((self.WORLD_WIDTH, self.WORLD_HEIGHT))
        self.worldrect = self.worldsurf.get_rect()
        self.worldrect.top = 5
        self.worldrect.centerx = self.SCREEN_WIDTH/2
        self.scoresurf = pygame.Surface((self.WORLD_WIDTH, 64))
        self.scorerect = self.scoresurf.get_rect()
        self.scorerect.top = 634
        self.scorerect.centerx = self.SCREEN_WIDTH/2
        #
        self.clock = pygame.time.Clock()

    def load_display_assets (self):
        self.screen = pygame.display.get_surface()
        self.f = Assets.f
        self.f24 = Assets.f24
        self.f28 = Assets.f28
        self.f96 = Assets.f96
        self.f36 = Assets.f36
        self.vector_explosion = Assets.vector_explosion
        self.vector_explosion_rect = self.vector_explosion.get_rect()

    def open_logs(self):
        self.log.open_gamelogs()

    def delay(self, ms):
        pygame.time.delay(ms)

    def now(self):
        return time.time()

    def play_sound(self, sound_id):
        if self.sounds_enabled:
            sounds.Sounds.play(sound_id)

    def draw_world(self):
        self.screen.fill((0,0,0))
        self.worldsurf.fill((0,0,0))
        self.scoresurf.fill((0,0,0))
        # Draws the game boundary.
        pygame.draw.rect(self.worldsurf, (0,255,0), (0,0, 710, 625), 1)
        for shell in self.shell_list:
            pyobj.draw_shell(shell, self.worldsurf)
        for missile in self.missile_list:
            pyobj.draw_missile(missile, self.worldsurf)
        #draws a small black circle under the fortress so we don't see the shell in the center
        pygame.draw.circle(self.worldsurf, (0,0,0), (355,315), 30)
        if self.fortress.exists:
            if self.fortress.alive:
                pyobj.draw_fortress(self.fortress, self.worldsurf)
            else:
                self.vector_explosion_rect.center = (self.fortress.position.x, self.fortress.position.y)
                self.worldsurf.blit(self.vector_explosion, self.vector_explosion_rect)
        if self.ship.alive:
            pyobj.draw_ship(self.ship, self.worldsurf)
        else:
            self.vector_explosion_rect.center = (self.ship.position.x, self.ship.position.y)
            self.worldsurf.blit(self.vector_explosion, self.vector_explosion_rect)
        pyobj.draw_score(self.score, self.scoresurf)
        pyobj.draw_hex(self.bighex, self.worldsurf)
        pyobj.draw_hex(self.smallhex, self.worldsurf)
        if self.mine.alive:
            pyobj.draw_mine(self.mine, self.worldsurf)
        if self.bonus.exists and self.bonus.visible:
            pyobj.draw_bonus(self.bonus, self.worldsurf)
        self.screen.blit(self.worldsurf, self.worldrect)
        self.screen.blit(self.scoresurf, self.scorerect)
        if int(self.config['draw_key_state']) == 1:
            self.draw_key_state()
        if int(self.config['draw_auto_state']) == 1:
            if self.ship.auto_turn:
                drawing.draw_tag(self.screen, 165, 20, "Turn", True, font=self.f)
            if self.ship.auto_thrust:
                drawing.draw_tag(self.screen, 230, 20, "Thrust", True, font=self.f)
        pygame.display.flip()

    def get_event(self):
        if self.model:
            if self.model.display_level > 0:
                # tell pygame to handle system events
                pygame.event.pump()
            return self.model.get_event(self)
        else:
            return pygame.event.get()

    def is_caret_key(self,event):
        return event.key == pygame.K_CARET or (event.key == pygame.K_6 and
                                               (event.mod&pygame.KMOD_LSHIFT or
                                                event.mod&pygame.KMOD_RSHIFT or
                                                event.mod&pygame.KMOD_SHIFT))

    def exit_prematurely(self):
        self.log.log_premature_exit()
        self.log.close_gamelogs()
        sys.exit()

    def process_input_events(self):
        """chief function to process keyboard events"""
        self.key_state.reset_tick()
        keys = []
        events = self.get_event()
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                keys.append([event.type, event.key, event.mod])
            if event.type == pygame.KEYDOWN:
                # self.keys_pressed[event.key] = True
                if self.is_caret_key(event):
                    self.log.add_event('got-caret')
                if event.key in (pygame.K_LMETA, pygame.K_RMETA, pygame.K_LALT, pygame.K_RALT, pygame.K_TAB):
                    print('PLEASE RETURN TO THE GAME IMMEDIATELY!!')
                if event.key == pygame.K_ESCAPE:
                    self.exit_prematurely()
                elif event.key in self.key_bindings:
                    self.press_key(self.key_bindings[event.key])
                elif event.key == pygame.K_0:
                    self.ship.auto_turn = not self.ship.auto_turn
                elif event.key == pygame.K_9:
                    self.ship.auto_thrust = not self.ship.auto_thrust
                elif event.key == pygame.K_8:
                    self.ship.auto_thrust_debug = not self.ship.auto_thrust_debug
            if event.type == pygame.KEYUP:
                # self.keys_pressed[event.key] = False
                if event.key in self.key_bindings:
                    self.release_key(self.key_bindings[event.key])
        b = [self.tinc]
        b.append(keys)
        self.log.write_keys(b)

    def finish(self):
        super(self.__class__, self).finish()
        exp.bonus += self.money

    def run(self):
        exp.log.slog('setup',{'condition': self.condition_name, 'session': self.session_name, 'game': self.game_name})
        exp.log.slog('begin')
        self.load_display_assets()
        self.start()
        self.screen.fill((0,0,0))
        time = pygame.time.get_ticks()
        while True:
            now = pygame.time.get_ticks()
            self.gameTimer.tick(now-time)
            time = now
            self.step_one_tick()
            self.clock.tick(self.fps)
            if self.cur_time >= int(self.config["game_time"]):
                break
        self.finish()
        exp.log.slog('end-game',{})
