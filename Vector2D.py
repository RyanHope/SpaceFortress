#Vector2D.py
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
#This class represents a basic 2 dimensional linear algebra vector.
from __future__ import division
import math


class Vector2D(object):
    def __init__(self, x=0, y=0):
        object.__init__(self)
        self.x = x
        self.y = y
        
    def norm(self):
        '''Returns the norm of the vector'''
        return math.sqrt(self.x**2 + self.y**2)
      
    def normalize(self):
        '''Normalizes the current vector'''
        norm = self.norm()
        self.x /= norm
        self.y /= norm

    def normal(self):
        '''Returns a normalized vector'''
        norm = self.norm()
        x = self.x/norm
        y = self.y/norm
        return Vector2D(x, y)

    def scalar_product(self, scalar):
        '''Returns the scalar product'''
        x = self.x * scalar
        y = self.y * scalar
        return Vector2D(x, y)

    def dot_product(self, hVector):
        '''Returns the dot product'''
        return (self.x * hVector.x) + (self.y * hVector.y)

    def projection(self, hVector):
        '''Returns the projection of a vector onto the current one'''
        return self.scalar_product(self.dot_product(hVector)/self.dot_product(self))

    @classmethod
    def parseVector(cls, hSource, hTarget):
        '''Returns the vector between two points'''
        X = hTarget.x - hSource.x
        Y = hTarget.y - hSource.y
        return  cls(X, Y)

if __name__ == '__main__':
    v = Vector2D(1, 1)
    print v