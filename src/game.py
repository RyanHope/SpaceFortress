from __future__ import division
from timer import Timer
import math

from Vector2D import Vector2D
import config
import ship
import fortress
import shell
import missile
import mine
import hexagon
import bonus
import score
import IFFIdentification
import log
import lisp

import time

class Game(object):
    def __init__(self,global_conf,game_name,game_number,games_in_session,config_path,model):
        # config
        self.datapath = config.get_datapath(global_conf)
        self.config_path = config_path
        self.config = config.read_conf(config.get_game_config_file(game_name),
                                       global_conf, self.config_path, ["#", "\n"])
        # model
        self.model = model
        #
        self.WORLD_WIDTH = 710
        self.WORLD_HEIGHT = 626
        # config variables
        self.condition_name = config.get_condition_name(self.config)
        self.session_name = config.get_session_name(self.config)
        self.game_name = game_name
        self.game_number = game_number
        self.games_in_session = games_in_session
        self.simulate = int(self.config["simulate"]) == 1
        self.image = int(self.config['image'])
        self.wind_magnitude = float(self.config["wind"][0])
        self.wind_direction = float(self.config["wind"][1])
        self.wind_magnitude_noise = float(self.config["wind_noise"][0])
        self.wind_direction_noise = float(self.config["wind_noise"][1])
        self.pre_game_screens = config.as_list(self.config,'pre_game_screens')
        self.post_game_screens = config.as_list(self.config,'post_game_screens')
        self.games_per_block = int(self.config['games_per_block'])
        if self.games_per_block > 0:
            self.block_start_screens = config.as_list(self.config,'block_start_screens')
            self.block_end_screens = config.as_list(self.config,'block_end_screens')
        self.session_start_screens = config.as_list(self.config,'session_start_screens')
        self.fps = 30.0
        if self.simulate and self.config.has_key('speedup'):
            self.fps *= self.config['speedup']
        # game objects
        self.cur_time = 0
        self.shell_list = []
        self.missile_list = []

        self.bonus = bonus.Bonus(self,self.config)
        self.fortress = fortress.Fortress(self,self.config)
        self.ship = ship.Ship(self,self.config)
        self.score = score.Score(self, self.config)
        self.IFFIdentification = IFFIdentification.IFFIdentification(self.config)
        self.bighex = hexagon.Hex(self, int(self.config["big_hex"]))
        self.smallhex = hexagon.Hex(self,int(self.config["small_hex"]))
        self.mine = mine.Mine(self,self.config)

        self.bonus.flag = True
        self.collisions = []
        # logging
        self.log = log.log(self.config['id'],config.get_datapath(global_conf),self.session_name,game_number)
        if self.simulate:
            self.log.open_simulate_logs()
        else:
            self.log.open_gamelogs()
        self.log.slog('setup',{'condition': self.condition_name, 'session': self.session_name, 'game': self.game_name})

    def compute_wind(self):
        if self.wind_magnitude_noise>0:
            mag_rand = random.uniform(-self.wind_magnitude_noise,self.wind_magnitude_noise)
        else:
            mag_rand = 0
        if self.wind_direction_noise>0:
            dir_rand = random.uniform(-self.wind_direction_noise,self.wind_direction_noise)
        else:
            dir_rand = 0
        mag = self.wind_magnitude + mag_rand
        direction = math.radians(self.wind_direction + dir_rand)
        return Vector2D(mag*math.cos(direction),mag*math.sin(direction))


    def update_score(self):
        self.IFFIdentification.check_for_timeout(self.log,self.score)
        if self.score.updatetimer.elapsed() > int(self.config["update_timer"]):
            self.score.updatetimer.reset()
            if float(self.config["min_speed_threshold"]) < (self.ship.velocity.x **2 + self.ship.velocity.y **2)**0.5 < float(self.config["max_speed_threshold"]):
                self.score.reward('vlcty', 'VLCTY_increment')
            else:
                self.score.penalize('vlcty', 'VLCTY_increment')
            if self.bighex.collide(self.ship):
                self.score.reward('cntrl', 'CNTRL_increment')
            else:
                self.score.reward_amt('cntrl', int(self.config["CNTRL_increment"])//2)

    def update_ship(self):
        self.ship.compute(self.fortress)                                  #move ship
        if self.smallhex.collide(self.ship):
            if int(self.config["explode_smallhex"]) == 1:
                self.ship.alive = False
                self.log.add_event('explode-smallhex')
            elif self.ship.small_hex_flag == False: #if ship hits small hex, bounce it back and subtract 5 points
                self.log.add_event('hit-small-hex')
                self.collisions.append('small-hex')
                self.ship.small_hex_flag = True
                self.ship.velocity.x = -self.ship.velocity.x
                self.ship.velocity.y = -self.ship.velocity.y
                if self.config["small_hex_score"] == 'cntrl':
                    self.score.penalize('cntrl', 'small_hex_penalty')
                elif self.config["small_hex_score"] == 'pnts':
                    self.score.penalize('pnts', 'small_hex_penalty')
                else:
                    raise Exception('dunno what score to penalize for small hex.')
        else:
            self.ship.small_hex_flag = False
        if not self.bighex.collide(self.ship):
            if int(self.config["explode_bighex"]) == 1:
                self.ship.alive = False
                self.log.add_event('explode-bighex')

    def update_fortress(self):
        """point fortress at ship, will fire if still for a short time"""
        if self.fortress.exists and self.fortress.deathtimer.elapsed() > 1000:
            self.fortress.alive = True
        self.fortress.compute(self)

    def update_mine(self):
        if not self.mine.exists:
            return

        if self.mine.alive:
            if self.mine.timer.elapsed() > self.mine.life_span:
                if self.mine.is_foe():
                    self.log.add_event('foe-timeout')
                else:
                    self.log.add_event('friend-timeout')
                self.IFFIdentification.add_mine(self.mine.is_foe(),self.score.intrvl)
                self.mine.kill()
                self.score.penalize('speed', 'mine_timeout_penalty')
            else:
                # Move mine, test to see if it hits ship.
                self.mine.compute()
                if self.mine.test_collision(self.ship):
                    self.IFFIdentification.add_mine(self.mine.is_foe(),self.score.intrvl,hit=True)
                    self.collisions.append('mine-ship')
                    if self.mine.is_foe():
                        self.log.add_event('foe-hit-ship')
                    else:
                        self.log.add_event('friend-hit-ship')
                    self.ship.take_damage()
                    if not self.ship.alive:
                        self.log.add_event('ship-destroyed')
                    self.mine.kill()
                    self.score.penalize('pnts', 'mine_hit_penalty')
        else:
            if self.mine.next_wake_up >= 0 and self.mine.timer.elapsed() > self.mine.next_wake_up:
                self.mine.spawn()
                self.log.add_event('spawn-%s'%self.mine.type())
                self.log.slog('spawn-%s'%self.mine.type())


    def update_shells(self):
        for i, shell in enumerate(self.shell_list):          #move any shells, delete if offscreen, tests for collision with ship
            shell.compute()
            if shell.position.x < 0 or shell.position.x > self.WORLD_WIDTH or shell.position.y < 0 or shell.position.y > self.WORLD_HEIGHT:
                del self.shell_list[i]
            if self.ship.alive:
                if shell.test_collision(self.ship):
                    self.log.add_event('shell-hit-ship')
                    self.collisions.append('shell')
                    del self.shell_list[i]
                    self.score.penalize('pnts', 'shell_hit_penalty')
                    self.ship.take_damage()
                    if not self.ship.alive:
                        self.log.add_event('ship-destroyed')
    
    def update_missiles(self):
        for i, missile in enumerate(self.missile_list):      #move any missiles, delete if offscreen
            missile.compute()
            if missile.position.x < 0 or missile.position.x > self.WORLD_WIDTH or missile.position.y < 0 or missile.position.y > self.WORLD_HEIGHT:
                del self.missile_list[i]
            if missile.test_collision(self.mine) and self.mine.alive: #missile hits mine?
                del self.missile_list[i]
                self.collisions.append('missile-mine')
                if self.mine.is_friend(): #friendly
                    if self.IFFIdentification.intervalflag or self.mine.is_tagged(): #false tag
                        self.log.add_event('hit-falsely-tagged-friend')
                    else:
                        self.log.add_event('hit-friend')
                        self.IFFIdentification.add_mine(False,self.score.intrvl,hit=True)
                        self.score.reward('pnts', 'energize_friend')
                        if self.fortress.exists: 
                            self.score.vlner += 1
                        # See how long mine has been alive. 0-100
                        # points if destroyed within 10 seconds, but
                        # timer runs for 5 seconds before mine appears
                        self.score.reward_amt('speed', 100 - 10 * int(self.mine.timer.elapsed()//1000))
                        self.mine.kill()
                elif self.mine.is_foe():
                    if self.mine.is_tagged():
                        self.log.add_event('hit-tagged-foe')
                        self.IFFIdentification.add_mine(True,self.score.intrvl,hit=True)
                        self.score.reward('pnts', 'destroy_foe')
                        # See how long mine has been alive. 0-100 points
                        # if destroyed within 10 seconds
                        self.score.reward_amt('speed', 100 - 10 * int(self.mine.timer.elapsed()//1000))
                        self.mine.kill()
                    else:
                        self.log.add_event('hit-untagged-foe')
        # enumerating a second time, so that when mine and fortress
        # overlap, we only remove the missile once.
        for i, missile in enumerate(self.missile_list):
            if missile.test_collision(self.fortress):
                del self.missile_list[i]
                if self.fortress.alive:
                    self.log.add_event('hit-fortress')
                    self.collisions.append('fortress')
                    if self.fortress.vulnerabilitytimer.elapsed() >= int(self.config["vlner_time"]):
                        if self.fortress.exists:
                            self.score.vlner += 1
                            self.log.add_event('vlner-increased')
                    if self.fortress.vulnerabilitytimer.elapsed() < int(self.config["vlner_time"]) and self.score.vlner >= (int(self.config["vlner_threshold"]) + 1):
                        self.log.add_event('fortress-destroyed')

                        self.fortress.alive = False
                        self.score.reward('pnts', 'destroy_fortress')
                        self.score.vlner = 0
                        if self.sounds_enabled:
                            self.sounds.explosion.play()
                        self.ship.alive = True
                        self.fortress.deathtimer.reset()
                    if self.fortress.vulnerabilitytimer.elapsed() < int(self.config["vlner_time"]) and self.score.vlner < (int(self.config["vlner_threshold"]) + 1):
                        self.log.add_event('vlner-reset')
                        self.score.vlner = 0
                        if self.sounds_enabled:
                            self.sounds.vlner_reset.play()
                    self.fortress.vulnerabilitytimer.reset()

    def update_bonus(self):
        if self.bonus.exists:
            self.bonus.update()

    def update_world(self):
        """chief function to update the world"""
        self.collisions = []
        self.update_score()
        self.update_ship()
        self.update_fortress()
        self.IFFIdentification.update(self)
        self.update_mine()
        self.update_shells()
        self.update_missiles()
        self.update_bonus()

    def get_world_state(self):
        """log current frame's data to text file. Note that first line contains foe mine designations
        format:
        system_clock game_time ship_alive? ship_x ship_y ship_vel_x ship_vel_y ship_orientation mine_alive? mine_x mine_y 
        fortress_alive? fortress_orientation [missile_x missile_y missile_orientation ...] [shell_x shell_y shell_orientation ...] bonus_symbol
        pnts cntrl vlcty vlner iff intervl speed shots thrust_key left_key right_key fire_key iff_key shots_key pnts_key"""
        game_time = self.cur_time
        if self.ship.alive:
            ship_alive = "y"
            ship_x = "%.3f"%(self.ship.position.x)
            ship_y = "%.3f"%(self.ship.position.y)
            ship_vel_x = "%.3f"%(self.ship.velocity.x)
            ship_vel_y = "%.3f"%(self.ship.velocity.y)
            ship_orientation = "%.1f"%(self.ship.orientation)
        else:
            ship_alive = "n"
            ship_x = "-"
            ship_y = "-"
            ship_vel_x = "-"
            ship_vel_y = "-"
            ship_orientation = "-"
        if self.mine.alive:
            mine_alive = "y"
            mine_x = "%.3f"%(self.mine.position.x)
            mine_y = "%.3f"%(self.mine.position.y)
        else:
            mine_alive = "n"
            mine_x = "-"
            mine_y = "-"
        if self.fortress.alive:
            fortress_alive = "y"
            fortress_orientation = "%.1f"%(self.fortress.orientation)
        else:
            fortress_alive = "n"
            fortress_orientation = "-"
        missile = '['
        for m in self.missile_list:
            missile += "%.3f %.3f %.1f "%(m.position.x, m.position.y, m.orientation)
        missile += ']'
        shell = '['
        for s in self.shell_list:
            shell += "%.3f %.3f %.1f "%(s.position.x, s.position.y, s.orientation)
        shell += ']'
        if self.bonus.visible:
            bonus = self.bonus.text
        else:
            bonus = "-"
        keys = self.keys_pressed#pygame.key.get_pressed()
        thrust_key = "y" if keys[self.thrust_key] else "n"
        left_key   = "y" if keys[self.left_turn_key] else "n"
        right_key  = "y" if keys[self.right_turn_key] else "n"
        fire_key   = "y" if keys[self.fire_key] else "n"
        iff_key    = "y" if keys[self.IFF_key] else "n"
        shots_key  = "y" if keys[self.shots_key] else "n"
        pnts_key   = "y" if keys[self.pnts_key] else "n"
        if self.score.iff == '':
            iff = '-'
        else:
            iff = self.score.iff
        return (game_time, ship_alive, ship_x, ship_y, ship_vel_x, ship_vel_y, ship_orientation, mine_alive, mine_x, mine_y, fortress_alive, fortress_orientation,\
                missile, shell, bonus, self.score.pnts, self.score.cntrl, self.score.vlcty, self.score.vlner, iff, self.score.intrvl,\
                self.score.speed, self.score.shots, thrust_key, left_key, right_key, fire_key, iff_key, shots_key, pnts_key)

    def get_world_state_for_model(self,screen_type):
        missiles = []
        for m in self.missile_list:
            missiles.append({'x': m.position.x, 'y': m.position.y,
                             'vx': m.velocity.x, 'vy': m.velocity.y,
                             'orientation': m.orientation})
        shells = []
        for s in self.shell_list:
            shells.append({'x': s.position.x, 'y': s.position.y,
                           'vx': s.velocity.x, 'vy': s.velocity.y,
                           'orientation': s.orientation})
        keys = []
        if self.keys_pressed[self.thrust_key]:
            keys.append(lisp.symbol('thrust'))
        if self.keys_pressed[self.left_turn_key]:
            keys.append(lisp.symbol('left'))
        if self.keys_pressed[self.right_turn_key]:
            keys.append(lisp.symbol('right'))
        if self.keys_pressed[self.fire_key]:
            keys.append(lisp.symbol('fire'))
        if self.keys_pressed[self.IFF_key]:
            keys.append(lisp.symbol('iff'))
        if self.keys_pressed[self.shots_key]:
            keys.append(lisp.symbol('shots'))
        if self.keys_pressed[self.pnts_key]:
            keys.append(lisp.symbol('pnts'))

        return {'screen-type': screen_type,
                'time': self.cur_time,
                'ship': {'alive': self.ship.alive,
                         'x': self.ship.position.x, 'y': self.ship.position.y,
                         'vx': self.ship.velocity.x, 'vy': self.ship.velocity.y,
                         'distance-from-fortress': (self.ship.position.copy()-self.fortress.position).norm(),
                         'angle': self.ship.angle_to_object(self.fortress),
                         'vdir': self.ship.velocity_angle_to_object(self.fortress),
                         'speed': self.ship.velocity.norm(),
                         'orientation': self.ship.orientation},
                'mine': {'x': self.mine.position.x, 'y': self.mine.position.y,
                         'vx': self.mine.velocity.x, 'vy': self.mine.velocity.y} if self.mine.exists and self.mine.alive else None,
                'fortress': {'alive': self.fortress.alive,
                             'x': self.fortress.position.x, 'y': self.fortress.position.y,
                             'orientation': self.fortress.orientation} if self.fortress.exists else None,
                'missiles': missiles,
                'shells': shells,
                'bonus': self.bonus.text if self.bonus.visible else None,
                'pnts': self.score.pnts, 'cntrl': self.score.cntrl, 'vlcty': self.score.vlcty, 'vlner': self.score.vlner,
                'iff': None if self.score.iff == '' else self.score.iff,
                'intrvl': self.score.intrvl or None,
                'speed': self.score.speed, 'shots': self.score.shots,
                'crew': self.score.crew_members,
                'keys': keys,
                'collisions': map(lisp.symbol, self.collisions)}

    def reset_position(self):
        """pauses the game and resets"""
        self.set_objects(self.get_world_state_for_model('game'))
        if not self.simulate:
            if self.sounds_enabled:
                self.sounds.explosion.play()
            if self.image:
                self.wait_and_eat_carets(1000)
            else:
                self.delay(1000)
        #self.minetimer.tick(1000)
        #self.updatetimer.tick(1000)
        #self.bonustimer.tick(1000)
        #self.intervaltimer.tick(1000)
        #self.fortresstimer.tick(1000)
        #self.fortressdeathtimer.tick(1000)
        self.fortress.timer.reset()

        #self.mine.timer.reset()
        #self.mine.alive = False
        #self.score.iff = ""
        self.ship.alive = True
        if self.fortress.exists:
            self.fortress.alive = True
        self.ship.position.x = 245
        self.ship.position.y = 315
        self.ship.velocity.x = float(self.config['ship_start_velocity'][0])
        self.ship.velocity.y = float(self.config['ship_start_velocity'][1])
        self.ship.orientation = 90

    def tick(self, mspf):
        self.mine.timer.tick(mspf)
        self.score.updatetimer.tick(mspf)
        self.bonus.timer.tick(mspf)
        self.IFFIdentification.timer.tick(mspf)
        self.fortress.vulnerabilitytimer.tick(mspf)
        self.fortress.deathtimer.tick(mspf)
        self.fortress.timer.tick(mspf)

    def set_objects(self,objects):
        if self.model:
            model.objects = copy.copy(objects)

    def step_one_tick(self):
        prev_time = self.cur_time
        self.cur_time = self.gameTimer.elapsed()
        if self.simulate:
            cur_rtime = 0.0
        else:
            cur_rtime = time.time()
        times = (self.cur_time, cur_rtime)
        self.tinc = self.cur_time - prev_time
        # Process Input
        self.set_objects(self.get_world_state_for_model('game'))
        self.process_input_events()
        self.update_world()
        self.log.write_events(times)
        self.log.write_game_state(times, self.get_world_state())
        # Draw the world!
        self.draw_world()
        # Increase clock time by the difference from the last frame
        self.tick(self.tinc)
        # Reset fortresss timer once ship has been destroyed
        if self.destroyed:
            self.fortress.timer.reset()
            self.destroyed = False
        # XXX: for some reason the fortress timer isn't properly
        # reset in reset_position so we need to do this little
        # dance.
        if self.ship.alive == False:
            self.reset_position()
            if self.score.crew_members > 0:
                self.score.crew_members -= 1
            else:
                self.score.penalize('pnts', 'ship_death_penalty')
            self.destroyed = True

    def start(self):
        self.log.slog('begin')
        self.gameTimer = Timer()
        self.destroyed = False

    def finish(self):
        self.log.slog('end-game',{})
        w.calculate_reward()
        w.log_score()
        w.log.close_gamelogs()
        w.log.rename_logs_completed()
