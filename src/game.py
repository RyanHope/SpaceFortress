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
import key_state

class Game(object):
    def __init__(self, conf, game_name, game_number):
        # config
        self.config = conf
        #
        self.WORLD_WIDTH = 710
        self.WORLD_HEIGHT = 626
        # config variables
        self.condition_name = config.get_condition_name(self.config)
        self.session_name = config.get_session_name(self.config)
        self.game_name = game_name
        self.game_number = game_number
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
        self.cur_time_override = None
        self.shell_list = []
        self.missile_list = []
        self.key_state = key_state.KeyState()

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
        self.log = log.game_log(self.config['id'],config.get_datapath(self.config),self.session_name,self.game_number)

    def press_key(self, key_id):
        if key_id in self.key_state.keys:
            self.log.add_event('hold-%s'%key_id)
            self.key_state.keys[key_id] = True
            self.key_state.events.append(key_state.Press(key_id))
        else:
            raise Exception('unknown key "%s"'%key_id)

    def release_key(self, key_id):
        if key_id in self.key_state.keys:
            self.log.add_event('release-%s'%key_id)
            self.key_state.keys[key_id] = False
            self.key_state.events.append(key_state.Release(key_id))
        else:
            raise Exception('unknown key "%s"'%key_id)

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

    def process_key_state(self):
        if self.wait_for_player and next((True for ev in self.key_state.events if isinstance(ev, key_state.Press)), False):
            self.wait_for_player = False
        for e in self.key_state.events:
            if isinstance(e, key_state.Press):
                if e.id in ['thrust', 'left', 'right']:
                    self.ship.motivator.press_key(e.id)
                elif e.id == 'fire':
                    self.fire_missile()
                elif e.id == 'iff':
                    self.IFFIdentification.keypress(self.log, self.score)
                elif e.id == 'shots':
                    if self.bonus.exists:
                        self.bonus.check_for_match(bonus.BONUS_SHOTS)
                elif e.id == 'pnts':
                    if self.bonus.exists:
                        self.bonus.check_for_match(bonus.BONUS_POINTS)
            elif isinstance(e, key_state.Release):
                if e.id in ['thrust', 'left', 'right']:
                    self.ship.motivator.release_key(e.id)

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
            self.collisions.append('small-hex')
            if int(self.config["explode_smallhex"]) == 1:
                self.ship.alive = False
                self.log.add_event('explode-smallhex')
            elif self.ship.small_hex_flag == False: #if ship hits small hex, bounce it back and subtract 5 points
                self.log.add_event('hit-small-hex')
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
                self.collisions.append('big-hex')
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


    def update_shells(self):
        for i, shell in enumerate(self.shell_list):          #move any shells, delete if offscreen, tests for collision with ship
            shell.compute()
            if shell.position.x < 0 or shell.position.x > self.WORLD_WIDTH or shell.position.y < 0 or shell.position.y > self.WORLD_HEIGHT:
                self.shell_list[i].alive = False
            if self.ship.alive:
                if shell.test_collision(self.ship):
                    self.log.add_event('shell-hit-ship')
                    self.collisions.append('shell')
                    self.shell_list[i].alive = False
                    self.score.penalize('pnts', 'shell_hit_penalty')
                    self.ship.take_damage()
                    if not self.ship.alive:
                        self.log.add_event('ship-destroyed')
        self.shell_list = [ s for s in self.shell_list if s.alive ]

    def fire_missile(self):
        if (self.mine.exists or self.fortress.exists) and not self.ship.firing_disabled:
            self.log.add_event('missile-fired')
            self.missile_list.append(missile.Missile(self))
            self.play_sound('missile-fired')
            if self.fortress.exists:
                if self.score.shots > 0:
                    self.score.shots -= 1
                    self.score.penalize('pnts', 'missile_penalty')
                else:
                    self.score.penalize('pnts', 'missile_debt_penalty')

    def update_missiles(self):
        for i, missile in enumerate(self.missile_list):      #move any missiles, delete if offscreen
            missile.compute()
            if missile.position.x < 0 or missile.position.x > self.WORLD_WIDTH or missile.position.y < 0 or missile.position.y > self.WORLD_HEIGHT:
                self.missile_list[i].alive = False
            elif missile.test_collision(self.mine) and self.mine.alive: #missile hits mine?
                self.missile_list[i].alive = False
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
            elif missile.test_collision(self.fortress):
                self.missile_list[i].alive = False
                if self.fortress.alive:
                    self.log.add_event('hit-fortress')
                    self.collisions.append('fortress')
                    if self.fortress.vulnerabilitytimer.elapsed() >= int(self.config["vlner_time"]):
                        if self.fortress.exists:
                            self.score.vlner += 1
                            self.log.add_event('vlner-increased')
                    elif self.fortress.vulnerabilitytimer.elapsed() < int(self.config["vlner_time"]) and self.score.vlner >= (int(self.config["vlner_threshold"]) + 1):
                        self.log.add_event('fortress-destroyed')
                        self.fortress.alive = False
                        self.score.reward('pnts', 'destroy_fortress')
                        self.score.vlner = 0
                        self.play_sound('explosion')
                        self.ship.alive = True
                        self.fortress.deathtimer.reset()
                    elif self.fortress.vulnerabilitytimer.elapsed() < int(self.config["vlner_time"]) and self.score.vlner < (int(self.config["vlner_threshold"]) + 1):
                        self.log.add_event('vlner-reset')
                        self.score.vlner = 0
                        self.play_sound('vlner-reset')
                    self.fortress.vulnerabilitytimer.reset()
        self.missile_list = [ m for m in self.missile_list if m.alive ]

    def update_bonus(self):
        if self.bonus.exists:
            self.bonus.update()

    def update_world(self):
        """chief function to update the world"""
        self.collisions = []
        self.process_key_state()
        if not self.wait_for_player:
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
        pnts cntrl vlcty vlner iff intervl speed shots thrust_key left_key right_key fire_key iff_key shots_key pnts_key game_active"""
        if self.cur_time_override != None:
            game_time = self.cur_time_override
        else:
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
        thrust_key = "y" if self.ship.motivator.thrust_flag else "n"
        left_key   = "y" if self.ship.motivator.turn_flag == 'left' else "n"
        right_key  = "y" if self.ship.motivator.turn_flag == 'right' else "n"
        fire_key   = "y" if self.key_state.keys['fire'] else "n"
        iff_key    = "y" if self.key_state.keys['iff'] else "n"
        shots_key  = "y" if self.key_state.keys['shots'] else "n"
        pnts_key   = "y" if self.key_state.keys['pnts'] else "n"
        if self.score.iff == '':
            iff = '-'
        else:
            iff = self.score.iff
        game_active = "n" if self.wait_for_player else "y"
        return (game_time, ship_alive, ship_x, ship_y, ship_vel_x, ship_vel_y, ship_orientation, mine_alive, mine_x, mine_y, fortress_alive, fortress_orientation,\
                missile, shell, bonus, self.score.pnts, self.score.cntrl, self.score.vlcty, self.score.vlner, iff, self.score.intrvl,\
                self.score.speed, self.score.shots, thrust_key, left_key, right_key, fire_key, iff_key, shots_key, pnts_key, game_active)

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
        if self.key_state.keys['thrust']:
            keys.append(lisp.symbol('thrust'))
        if self.key_state.keys['left']:
            keys.append(lisp.symbol('left'))
        if self.key_state.keys['right']:
            keys.append(lisp.symbol('right'))
        if self.key_state.keys['fire']:
            keys.append(lisp.symbol('fire'))
        if self.key_state.keys['iff']:
            keys.append(lisp.symbol('iff'))
        if self.key_state.keys['shots']:
            keys.append(lisp.symbol('shots'))
        if self.key_state.keys['pnts']:
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
                'active': not self.wait_for_player,
                'keys': keys,
                'collisions': map(lisp.symbol, self.collisions)}

    def get_total_score(self):
        total = 0
        if 'pnts' in self.config['active_scores']:
            total += self.score.pnts
        if 'cntrl' in self.config['active_scores']:
            total += self.score.cntrl
        if 'vlcty' in self.config['active_scores']:
            total += self.score.vlcty
        if 'speed' in self.config['active_scores']:
            total += self.score.speed
        if 'crew' in self.config['active_scores']:
            total += self.score.crew_members * int(self.config['crew_member_points'])
        return total

    def calculate_reward(self):
        total = self.get_total_score()
        b = int(self.config['bonus_per_game'])
        p = int(self.config['bonus_max_points_per_game'])
        # round to the nearest integer to give the poor students a break.
        self.money = min(b, max(0, int(round(total / float(p) * b))));

    def format_money(self, amount=None):
        if amount == None:
            amount = self.money
        return "%d.%02d"%(amount/100,amount%100)

    def log_score(self):
        total = self.get_total_score()
        if 'pnts' in self.config['active_scores']:
            self.log.glog("pnts score %d"%self.score.pnts)
        if 'cntrl' in self.config['active_scores']:
            self.log.glog("cntrl score %d"%self.score.cntrl)
        if 'vlcty' in self.config['active_scores']:
            self.log.glog("vlcty score %d"%self.score.vlcty)
        if 'speed' in self.config['active_scores']:
            self.log.glog("speed score %d"%self.score.speed)
        if 'crew' in self.config['active_scores']:
            self.log.glog("crew score %d"%(self.score.crew_members*int(self.config['crew_member_points'])))
        self.log.glog("total score %d"%total)
        self.log.glog("raw pnts %d"%self.score.raw_pnts)
        self.log.glog("bonus earned $%s"%self.format_money())

    def reset_position(self):
        """pauses the game and resets"""
        self.set_objects(self.get_world_state_for_model('game'))
        if not self.simulate:
            self.play_sound('explosion')
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
        self.fortress.vulnerabilitytimer.reset(int(self.config["vlner_time"]))
        
        #self.mine.timer.reset()
        #self.mine.alive = False
        #self.score.iff = ""
        self.ship.alive = True
        if self.fortress.exists:
            self.fortress.alive = True
            self.fortress.orientation = 180
        self.ship.reset()
        self.reset_event_queue()
        self.wait_for_player = int(self.config['wait_for_player'])

    def tick(self, mspf):
        if not self.wait_for_player:
            self.mine.timer.tick(mspf)
            self.score.updatetimer.tick(mspf)
            self.bonus.timer.tick(mspf)
            self.IFFIdentification.timer.tick(mspf)
            self.fortress.vulnerabilitytimer.tick(mspf)
            self.fortress.deathtimer.tick(mspf)
            self.fortress.timer.tick(mspf)

    def set_objects(self,objects):
        pass

    def step_one_tick(self):
        prev_time = self.cur_time
        self.cur_time = self.gameTimer.elapsed()
        times = (self.cur_time, self.now())
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
        self.gameTimer = Timer()
        self.destroyed = False
        self.wait_for_player = int(self.config['wait_for_player'])
        self.open_logs()

    def finish(self):
        self.calculate_reward()
        self.log_score()
        self.log.close_gamelogs()
        self.log.rename_logs_completed()
