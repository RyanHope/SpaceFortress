#timer.py
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
import pygame

class Timer(object):
    """basic game timer"""
    def __init__(self, app):
        super(Timer, self).__init__()
        self.start_time = pygame.time.get_ticks()
        
    def elapsed(self):
        """time elapsed since timer created"""
        return (pygame.time.get_ticks() - self.start_time)
        
    def reset(self):
        """resets timer to current time"""
        self.start_time = pygame.time.get_ticks()
        
    def check(self):
        pass
        
class CountdownTimer(Timer):
    """timer that does something upon expiration"""
    def __init__(self, time, function):
        super(CountdownTimer, self).__init__()
        self.time = time
        self.function = function
        
    def check(self):
        """determines whether timer triggers yet"""
        if (pygame.time.get_ticks() - self.start_time) >= self.time:
            self.function()
            return True
        else:
            return False
