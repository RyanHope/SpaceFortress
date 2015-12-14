from __future__ import division
from Vector2D import Vector2D
import math
import random
import object as obj

class Ship(obj.Object):
    """represents the fortress object that typically appears in the center of the worldsurf"""
    def __init__(self, app,config):
        super(Ship, self).__init__()
        self.app = app
        self.collision_radius = 10
        self.position.x = 245
        self.position.y = 315
        self.orientation = 90
        self.start_position.x = 245
        self.start_position.y = 315
        self.velocity.x = float(config['ship_start_velocity'][0])
        self.velocity.y = float(config['ship_start_velocity'][1])
        self.missile_capacity = 100
        self.missile_count = 100
        self.active_missile_limit = 5
        self.active_missile_count = 0
        self.last_fired = -100
        self.last_IFF_value = 0
        self.notify_mine_IFF = False
        self.world_wrap_flag = False
        self.thrust_flag = False
        self.thrust = 0
        self.turn_flag = False
        self.fire_flag = False
        self.firing_disabled = False
        self.turn_speed = int(config["ship_turn_speed"])
        self.auto_turn = int(config['ship_auto_turn'])
        self.auto_thrust = int(config['ship_auto_thrust'])
        self.auto_thrust_min_radius = 45
        self.auto_thrust_max_radius = 70
        self.auto_thrust_debug = int(config['auto_thrust_debug'])
        self.auto_thrust_outside_threshold = False
        self.acceleration = 0
        self.acceleration_factor = float(config["ship_acceleration"])
        self.acceleration_noise = float(config["ship_acceleration_noise"])
        self.velocity_ratio = 0.65
        self.fire_interval = 5
        self.threshold_factor = 0
        self.autofire = False
        self.nochange = False
        self.health = int(config["ship_hit_points"])
        self.max_vel = int(config["ship_max_vel"])
        self.set_alive = True
        self.set_invulnerable = False
        self.half_size = 30 #??? What IS this about?
        # self.center_line = sf_object.line.Line()
        # self.r_wing_line = sf_object.line.Line()
        # self.l_wing_line = sf_object.line.Line()
        self.small_hex_flag = False #did we hit the small hex?
        self.wrap_penalty_score = config['wrap_score']
        if not self.wrap_penalty_score in ('cntrl','pnts'):
            raise Exception("wrap penalty must be taken from cntrl or pnts. Invalid score id: %s"%self.wrap_penalty_score)

    def angle_to_object(self,object):
	"""compute angle from direction to ship"""
        # orientation is in textbook euclidean space where Y increases
        # as you go up the screen. But in reality Y decreases up the
        # screen, meaning its upside down. So adjust the vectors to be
        # in orientation's space.
	actual = math.degrees(((object.position.copy()-self.position)*Vector2D(1,-1)).angle())
	diff = self.orientation - actual
	if diff > 180.0:
	    diff = diff - 360.0
	if diff < -180.0:
	    diff = diff + 360.0
	return diff

    def velocity_angle_to_object(self, object):
        if self.velocity.norm() <> 0:
            # I guess velocity is in textbook euclidean space, too. So
            # we gotta put the position vectors in that same space to
            # compare the angles.
            o_angle = math.degrees(((object.position.copy()-self.position)*Vector2D(1,-1)).angle())
            v_angle = math.degrees(self.velocity.angle())
            diff = v_angle - o_angle
            if diff > 180.0:
                diff = diff - 360.0
            if diff < -180.0:
                diff = diff+ 360.0
            return diff
        else:
            return None

    def distance_to_fortress(self):
        return (self.app.fortress.position-self.position).norm()
    
    def angle_to_fortress(self):
        return math.degrees(((self.app.fortress.position.copy()-self.position)*Vector2D(1,-1)).angle())

    def angle_to_fortress2(self):
        return math.degrees((self.app.fortress.position-self.position).angle())

    def distance_between_angles(self, a1, a2):
        a = (a1-a2)%360
        if a > 180:
            return 360-a
        else:
            return a

    def distance_from_two_angles(self, a, min_angle, max_angle):
        return min(self.distance_between_angles(a, min_angle),
                   self.distance_between_angles(a, max_angle))

    def between_angles(self, a, angle1, angle2):
        angle1 %= 360
        angle2 %= 360
        a %= 360
        if (angle1-angle2)%360 > 180:
            (angle1,angle2) = (angle2, angle1)
        if angle2 > angle1:
            return a >= angle2 or a <= angle1
        else:
            return a >= angle2 and a <= angle1

    def accelerate_vector(self, vel):
        vel.x += self.acceleration_factor * math.cos(math.radians(self.orientation))
        if vel.x > self.max_vel:
            vel.x = self.max_vel
        elif vel.x < -self.max_vel:
            vel.x = -self.max_vel
        vel.y += self.acceleration_factor * math.sin(math.radians(self.orientation))
        if vel.y > self.max_vel:
            vel.y = self.max_vel
        elif vel.y < -self.max_vel:
            vel.y = -self.max_vel
        return vel

    def detect_thrustable_conditions(self):
        d = self.distance_to_fortress()
        a = self.angle_to_fortress2()
        if d >= self.auto_thrust_min_radius:
            self.min_angle = (a + math.degrees(math.asin(self.auto_thrust_min_radius / -d)))%360
        if d >= self.auto_thrust_max_radius:
            self.max_angle = (a + math.degrees(math.asin(self.auto_thrust_max_radius / -d)))%360
        # if self.position.x < self.app.fortress.position.x and self.position.y > self.app.fortress.position.y:
        #     self.min_angle += 180
        #     self.max_angle += 180

        self.both = d >= self.auto_thrust_max_radius and d >= self.auto_thrust_min_radius
        self.vel_angle = math.degrees((self.velocity*Vector2D(1,-1)).angle())
        vel = self.accelerate_vector(self.velocity.copy())
        self.after_thrust_angle = math.degrees((vel*Vector2D(1,-1)).angle())
        # self.between = self.between_angles(-self.orientation, self.min_angle, self.max_angle)
        self.between = self.between_angles(self.vel_angle, self.min_angle, self.max_angle)
        self.d_before = self.distance_from_two_angles(self.vel_angle, self.min_angle, self.max_angle)
        self.d_after = self.distance_from_two_angles(self.after_thrust_angle, self.min_angle, self.max_angle)
        #print("o:%.1f f:%.1f %.1f %.1f min:%.1f max:%.1f %.1f %.1f %d"%(self.orientation, self.angle_to_fortress2(), self.vel_angle, self.after_thrust_angle, self.min_angle, self.max_angle, self.d_before, self.d_after, self.d_after < self.d_before))
        return self.both and not self.between and vel.norm() < 1.8 and self.d_after < self.d_before

    def old_detect_thrustable_conditions(self):
        """Return True if conditions are right for an auto-thrust."""
        # Check the ship angle
        a = self.angle_to_fortress()
        dx = math.cos(math.radians(a))
        dy = math.sin(math.radians(a))
        top = self.app.fortress.position + Vector2D(dy,dx).normal().scalar_product(self.app.fortress.collision_radius+20)
        bot = self.app.fortress.position + Vector2D(-dy,-dx).normal().scalar_product(self.app.fortress.collision_radius+20)
        top_a = math.degrees(((top-self.position)*Vector2D(1,-1)).angle())
        bot_a = math.degrees(((bot-self.position)*Vector2D(1,-1)).angle())
        if top_a < 90 and bot_a > 270:
            angle_ok = self.orientation <= top_a or self.orientation >= bot_b
        elif top_a > 270 and bot_a < 90:
            angle_ok = self.orientation <= bot_a or self.orientation >= top_a
        else:
            angle_ok = self.orientation >= min(top_a, bot_a) and self.orientation <= max(top_a, bot_a)
        # check the ship velocity
        v = (self.app.fortress.position - self.position)*Vector2D(-1,1)
        (v.x, v.y) = (v.y, v.x)
        tangent_a = math.degrees(v.angle())
        vel_a = math.degrees((self.velocity*Vector2D(1,-1)).angle())
        delta_a = (tangent_a - vel_a)%360
        # Add progressively more slop in the velocity threshold as we
        # get closer to the fortress to encourage a stable orbit.
        if self.auto_thrust_outside_threshold:
            velocity_ok = delta_a > 0 and delta_a < 180
            if not velocity_ok:
                self.auto_thrust_outside_threshold = False
        else:
            min_pad = 0
            max_pad = 10 # 20
            percent = (self.position - self.app.fortress.position).norm() / self.app.bighex.radius
            pad = min_pad + (max_pad-min_pad)*(1-percent)
            velocity_ok = delta_a > pad and delta_a < 180-pad
            if velocity_ok:
                self.auto_thrust_outside_threshold = True

        return (angle_ok and velocity_ok, angle_ok, velocity_ok, top, bot, tangent_a, vel_a)

    def compute(self, fortress):
        """updates ship"""
        if self.auto_turn:
            self.orientation = int(self.angle_to_fortress())
        else:
            if self.turn_flag == 'right':
                self.orientation = (self.orientation - self.turn_speed) % 360
            elif self.turn_flag == 'left':
                self.orientation = (self.orientation + self.turn_speed) % 360
        #thrust is only changed if joystick is engaged. Thrust is calculated while processing joystick input
        #self.acceleration = self.thrust * -0.3
        if self.auto_thrust:
            self.thrust_flag = self.detect_thrustable_conditions()

        if self.thrust_flag == True:
            self.acceleration = self.acceleration_factor
            # it uses random so every time the player accelerates he
            # changes the next random number, affecting the bonus and
            # mines. This is annoying when the noise is 0 (turned off).
            if self.acceleration_noise > 0:
                self.acceleration_factor += random.uniform(-self.acceleration_noise,self.acceleration_noise)
        else:
            self.acceleration = 0
        wind = self.app.compute_wind()
        self.velocity.x += self.acceleration * math.cos(math.radians(self.orientation)) + wind.x
        if self.velocity.x > self.max_vel:
            self.velocity.x = self.max_vel
        elif self.velocity.x < -self.max_vel:
            self.velocity.x = -self.max_vel
        self.velocity.y += self.acceleration * math.sin(math.radians(self.orientation)) + wind.y
        if self.velocity.y > self.max_vel:
            self.velocity.y = self.max_vel
        elif self.velocity.y < -self.max_vel:
            self.velocity.y = -self.max_vel
        self.position.x += self.velocity.x
        self.position.y -= self.velocity.y
	wrapped = False
        if self.position.x > self.app.WORLD_WIDTH:
            self.position.x = 0
            #self.app.log.write("# wrapped right\n")
	    wrapped = True
        if self.position.x < 0:
            self.position.x = self.app.WORLD_WIDTH
            #self.app.log.write("# wrapped left\n")
	    wrapped = True
        if self.position.y > self.app.WORLD_HEIGHT:
            self.position.y = 0
            #self.app.log.write("# wrapped down\n")
	    wrapped = True
        if self.position.y < 0:
            self.position.y = self.app.WORLD_HEIGHT
            #self.app.log.write("# wrapped up\n")
	    wrapped = True
	if wrapped:
	    self.app.log.add_event('wrapped')
            if self.wrap_penalty_score == 'cntrl':
                self.app.score.penalize('cntrl', 'wrap_penalty')
            elif self.wrap_penalty_score  == 'pnts':
                self.app.score.penalize('pnts', 'wrap_penalty')
