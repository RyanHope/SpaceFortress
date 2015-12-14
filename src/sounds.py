import pygame

class Sounds(object):
    """collection of game sounds"""
    def __init__(self):
        super(Sounds, self).__init__()
        self.shell_fired = pygame.mixer.Sound("sounds/ShellFired.wav")
        self.missile_fired = pygame.mixer.Sound("sounds/MissileFired.wav")
        self.explosion = pygame.mixer.Sound("sounds/ExpFort.wav")
        self.collision = pygame.mixer.Sound("sounds/Collision.wav")
        self.vlner_reset = pygame.mixer.Sound("sounds/VulnerZeroed.wav")
        self.beep_high = pygame.mixer.Sound("sounds/beep-high.wav")
        self.beep_low = pygame.mixer.Sound("sounds/beep-low.wav")
        self.warn_high = pygame.mixer.Sound("sounds/warn-high.wav")
        self.warn_low = pygame.mixer.Sound("sounds/warn-low.wav")
