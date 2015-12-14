from __future__ import division
from Vector2D import Vector2D
import math
import random
import object as obj

class Missile(obj.Object):
    """represents the weapon fired by the ship"""
    def __init__(self, app):
        super(Missile, self).__init__()
        self.app = app
        self.orientation = self.app.ship.orientation
        self.position.x = self.app.ship.position.x
        self.position.y = self.app.ship.position.y
        self.collision_radius = 5
        self.speed = int(app.config["missile_speed"])
        self.velocity.x = math.cos(math.radians((self.orientation) % 360)) * self.speed
        self.velocity.y = -math.sin(math.radians((self.orientation) % 360)) * self.speed

    def compute(self):
        """calculates new position of ship's missile"""
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

    def collides_with(self, sf_object):
        """determines if mine is colliding with a particular object"""
        incx = math.cos(math.radians((self.orientation) % 360)) # "incremental x" - how much it moves with speed = 1
        incy = -math.sin(math.radians((self.orientation) % 360)) # "incremental y" - how much it moves with speed = 1
        for i in range(1, self.speed + 1):
            tempx = self.position.x + incx * i #test position
            tempy = self.position.y + incy * i
            tempdist = math.sqrt(((tempx - sf_object.position.x) ** 2) + ((tempy - sf_object.position.y) ** 2))
            if tempdist <= self.collision_radius + sf_object.collision_radius:
                return 1
        return 0

