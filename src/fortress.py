from __future__ import division
from Vector2D import Vector2D
import math
import random
import timer
import shell
import object as obj

class Fortress(obj.Object):
    def __init__(self, app, config):
        super(Fortress, self).__init__()
        self.app = app
        self.position.x = 355
        self.position.y = 315
        self.start_position.x = 355
        self.start_position.y = 315
        self.collision_radius = 18 #I'm making this up
        self.last_orientation = self.orientation 
        self.shell_alive = False
        self.automated = True
        self.fire_lock = 22
        self.thrust_flag = False #almost guaranteed that we won't be using this <mcd>
        self.turn_flag = False #won't use - just for manual fortress control <mcd>
        self.fire_flag = False #why am I wasting my time with these? <mcd>
        self.target = None
        self.target_str = "" #java code has two attributes called target with Hungarian notation. BAH <mcd>
        self.turn_threshold = 1
        self.double_shot_interval = 1
        self.lock_interval = 1
        self.thrust_speed = 0.0
        self.turn_speed = 0
        self.velocity_ratio = 0.0 #bullocks! The fortress doesn't move! <mcd>
        self.extra_damage_limit = 1000
        self.half_size = 30 #I can't find what this is supposed to be - it's used heavily in RSF's compute_fortess()
        self.timer = timer.Timer()
        self.deathtimer = timer.Timer()
        self.vulnerabilitytimer = timer.Timer()
        self.sector_size = int(config["fortress_sector_size"])
        self.lock_time = int(config["fortress_lock_time"])
        self.exists = int(config["fortress_enable"]) == 1
        self.alive = self.exists

    def compute(self, app):
        """determines orientation of fortress"""
	if not self.exists:
	    return
        if app.ship.alive:
            self.orientation = self.to_target_orientation(app.ship) // self.sector_size * self.sector_size #integer division truncates
        if self.orientation != self.last_orientation:
            self.last_orientation = self.orientation
            self.timer.reset()
        if self.timer.elapsed() >= self.lock_time and app.ship.alive and app.fortress.alive:
            #app.log.write("# fortress fired\n")
	    app.log.add_event('fortress-fired')
            self.fire(app.ship)
            self.timer.reset()

    def fire(self, ship):
        if self.app.sounds_enabled:
            self.app.sounds.shell_fired.play()
        self.app.shell_list.append(shell.Shell(self.app, self.to_target_orientation(ship)))
