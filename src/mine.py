from __future__ import division
from Vector2D import Vector2D
import math
import random
import string
import object as obj
import timer

class Mine(obj.Object):
    """represents the friend or foe mine object"""
    def __init__(self, app, config):
        super(Mine, self).__init__()
        self.position.x = 600
        self.position.y = 400
        self.app = app
        self.speed = int(config["mine_speed"])
        self.health = 1
        self.alive = False
        self.collision_radius = 20
        self.foe_probability = float(config["mine_probability"])
        self.life_span = int(config["mine_timeout"])
        self.sleep_span = int(config["mine_spawn"])
        self.sleep_span_noise = int(config["mine_spawn_noise"])
        if config.has_key('mine_times'):
            self.mine_times = config['mine_times']
            if not isinstance(self.mine_times,list):
                self.mine_times = [self.mine_times]
            self.mine_times = map(int,self.mine_times)
        else:
            self.mine_times = None
        if config.has_key('mine_types'): # JPB120327
            self.mine_types = config['mine_types']
            if not isinstance(self.mine_types,list):
                self.mine_types = [self.mine_types]
            #self.mine_types = map(int,self.mine_types)
        else:
            self.mine_types = None
        self.minimum_spawn_distance = 320
        self.maximum_spawn_distance = 640
        self.iff_lower_bound = int(config["intrvl_min"])
        self.iff_upper_bound = int(config["intrvl_max"])
        self.num_foes = int(config["num_foes"])
        self.letters = list(string.letters[26:]) #list of uppercase letters
        self.exists = int(config["mine_enable"]) == 1
        self.foeness_group_size = int(config['mine_probability_group_size'])
        if self.foeness_group_size > 0:
            self.populate_foeness_list()
        self.generate_foes()
        self.timer = timer.Timer()
        self.schedule_wake_up()

    def is_foe(self):
        return self.app.score.iff in self.foe_letters

    def is_friend(self):
        return self.app.score.iff in self.letters

    def type(self):
        return 'foe' if self.is_foe() else 'friend'

    def is_tagged(self):
        return self.iff_lower_bound <= self.app.score.intrvl <= self.iff_upper_bound

    def generate_foes(self):
        """determine which mine designations are 'foes'"""
        self.foe_letters = random.sample(self.letters, self.num_foes)
        self.foe_letters.sort()
        for each in self.foe_letters:
            self.letters.remove(each)

    def generate_new_position(self):
        """chooses random location to place mine"""
        self.position.x = random.random() * (self.app.WORLD_WIDTH - 40) + 20
        self.position.y = random.random() * (self.app.WORLD_HEIGHT - 40) + 20

    def schedule_wake_up(self):
        if isinstance(self.mine_times,list):
            if len(self.mine_times)>0:
                time = self.mine_times.pop(0)
                self.next_wake_up = max(time - self.app.cur_time,0)
            else:
                # negative number means never
                self.next_wake_up = -1
        else:
            self.next_wake_up = self.sleep_span + random.randint(-self.sleep_span_noise,self.sleep_span_noise)

    def kill(self):
        """Get rid of the mine. It hit the player, timed out, or got shot."""
        self.alive = False
        self.app.score.intrvl = 0
        self.app.score.iff = ""
        self.app.intervalflag = False
        self.timer.reset()
        self.schedule_wake_up()

    def populate_foeness_list(self):
        # Predetermine mine types before hand when possible
        cap = int(self.foeness_group_size*self.foe_probability)
        self.foeness_list = [x<cap for x in xrange(self.foeness_group_size)]
        random.shuffle(self.foeness_list)

    def spawn(self):
        """resets mine - makes alive, places it a distance away from the ship, gets IFF tag"""
        self.alive = True
        
        if isinstance(self.mine_types,list):
    	    foe = self.mine_types.pop(0) == "foe"
            #print foe
        else:
            if self.foeness_group_size > 0:
                if len(self.foeness_list) == 0:
                    self.populate_foeness_list()
                foe = self.foeness_list.pop(0)
            else:
                foe = random.random() < self.foe_probability
        
        if foe:
            self.app.score.iff = random.sample(self.foe_letters, 1)[0]
        else:
            self.app.score.iff = random.sample(self.letters, 1)[0]
        self.generate_new_position()
        while self.get_distance_to_object(self.app.ship) < 400:
            self.generate_new_position()
        self.timer.reset()

    def compute(self):
        """calculates new position of mine"""
        self.velocity.x = math.cos(math.radians((self.to_target_orientation(self.app.ship)) % 360)) * self.speed
        self.velocity.y = -math.sin(math.radians((self.to_target_orientation(self.app.ship)) % 360)) * self.speed
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        
