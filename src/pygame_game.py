from __future__ import division
import pygame
import os
import sys
import sounds
import game

import missile

import pygame_objects as pyobj

class Game(game.Game):
    def __init__(self,global_conf,game_name,game_number,games_in_session,config_path,model):
        super(self.__class__, self).__init__(global_conf,game_name,game_number,games_in_session,config_path,model)
        # input
        self.thrust_key = eval("pygame.K_%s"%self.config["thrust_key"])
        self.left_turn_key = eval("pygame.K_%s"%self.config["left_turn_key"])
        self.right_turn_key = eval("pygame.K_%s"%self.config["right_turn_key"])
        self.fire_key = eval("pygame.K_%s"%self.config["fire_key"])
        self.IFF_key = eval("pygame.K_%s"%self.config["IFF_key"])
        self.shots_key = eval("pygame.K_%s"%self.config["shots_key"])
        self.pnts_key = eval("pygame.K_%s"%self.config["pnts_key"])
        self.keys_pressed = {self.thrust_key:False, self.left_turn_key:False,
                             self.right_turn_key:False, self.fire_key:False,
                             self.IFF_key:False, self.shots_key:False,
                             self.pnts_key:False}
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
        #
        if self.sounds_enabled:
            self.sounds = sounds.Sounds()

    def load_display_assets (self):
        self.screen = pygame.display.get_surface()
        self.f = pygame.font.Font("fonts/freesansbold.ttf", 14)
        self.f24 = pygame.font.Font("fonts/freesansbold.ttf", 20)
        self.f28 = pygame.font.Font("fonts/freesansbold.ttf", 28)
        self.f96 = pygame.font.Font("fonts/freesansbold.ttf", 72)
        self.f36 = pygame.font.Font("fonts/freesansbold.ttf", 36)
        self.vector_explosion = pygame.image.load("gfx/exp.png")
        self.vector_explosion.set_colorkey((0, 0, 0))
        self.vector_explosion_rect = self.vector_explosion.get_rect()

    def delay(self, ms):
        pygame.time.delay(ms)

    def play_sound(self,sound):
        if self.sounds_enabled:
            self.sounds.explosion.play()

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
        keys = []
        if self.simulate:
            events = map(self.to_event,self.keys)
            for event in self.get_event():
                #print(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    sys.exit()
        else:
            events = self.get_event()
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                keys.append([event.type, event.key, event.mod])
            if event.type == pygame.KEYDOWN:
                self.keys_pressed[event.key] = True
                if self.is_caret_key(event):
                    self.log.slog('got-caret')
                if event.key in (pygame.K_LMETA, pygame.K_RMETA, pygame.K_LALT, pygame.K_RALT, pygame.K_TAB):
                    print('PLEASE RETURN TO THE GAME IMMEDIATELY!!')
                if event.key == pygame.K_ESCAPE:
                    self.exit_prematurely()
                if event.key == self.right_turn_key:
                    self.ship.turn_flag = 'right'
                    self.log.add_event('hold-right')
                if event.key == self.left_turn_key:
                    self.ship.turn_flag = 'left'
                    self.log.add_event('hold-left')
                if event.key == self.thrust_key:
                    self.ship.thrust_flag = True
                    self.log.add_event('hold-thrust')
                if event.key == self.fire_key:
                    self.log.add_event('hold-fire')
                    if (self.mine.exists or self.fortress.exists) and not self.ship.firing_disabled:
                        self.log.add_event('missile-fired')
                        self.missile_list.append(missile.Missile(self))
                        if self.sounds_enabled:
                            self.sounds.missile_fired.play()
                        if self.fortress.exists:
                            if self.score.shots > 0:
                                self.score.shots -= 1
                                self.score.penalize('pnts', 'missile_penalty')
                            else:
                                self.score.penalize('pnts', 'missile_debt_penalty')
                if event.key == self.IFF_key:
                    self.log.add_event('hold-iff')
                    if self.mine.exists and self.mine.alive:
                        self.IFFIdentification.keypress(self.log,self.score)
                if event.key == self.shots_key and self.bonus.exists:
                    self.log.add_event('hold-shots')
                    self.bonus.check_for_match(bonus.BONUS_SHOTS)
                if event.key == self.pnts_key and self.bonus.exists:
                    self.log.add_event('hold-pnts')
                    self.bonus.check_for_match(bonus.BONUS_POINTS)
                if event.key == pygame.K_0:
                    self.ship.auto_turn = not self.ship.auto_turn
                if event.key == pygame.K_9:
                    self.ship.auto_thrust = not self.ship.auto_thrust
                if event.key == pygame.K_8:
                    self.ship.auto_thrust_debug = not self.ship.auto_thrust_debug

            if event.type == pygame.KEYUP:
                self.keys_pressed[event.key] = False
                if event.key == self.left_turn_key:
                    self.log.add_event('release-left')
                    if self.ship.turn_flag == 'left':
                        self.ship.turn_flag = False
                if event.key == self.right_turn_key:
                    self.log.add_event('release-right')
                    if self.ship.turn_flag == 'right':
                        self.ship.turn_flag = False
                if event.key == self.thrust_key:
                    self.log.add_event('release-thrust')
                    self.ship.thrust_flag = False
                if event.key == self.fire_key:
                    self.log.add_event('release-fire')
                if event.key == self.IFF_key:
                    self.log.add_event('release-iff')
                if event.key == self.shots_key:
                    self.log.add_event('release-shots')
                if event.key == self.pnts_key:
                    self.log.add_event('release-pnts')
        b = [self.tinc]
        b.append(keys)
        self.log.write_keys(b)

    def game_loop(self):
        self.start()
        self.screen.fill((0,0,0))
        time = pygame.time.get_ticks()
        while True:
            # Timing
            if self.simulate:
                tinc = self.simulate_get_keys()
                self.gameTimer.tick(tinc)
            elif self.model:
                if self.destroyed:
                    self.gameTimer.tick(1033)
                else:
                    self.gameTimer.tick(33)
            else:
                now = pygame.time.get_ticks()
                self.gameTimer.tick(now-time)
                time = now
            self.step_one_tick()
            if not self.model:
                self.clock.tick(self.fps)
            if self.cur_time >= int(self.config["game_time"]):
                break
