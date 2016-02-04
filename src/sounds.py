import pygame
import os

class Sounds(object):
    """collection of game sounds"""
    def __init__(self):
        pass

    @staticmethod
    def load():
        Sounds.sounds = {}
        for root, dirs, files in os.walk("sounds/"):
            for f in files:
                (head, tail) = os.path.split(f)
                (name, ext) = os.path.splitext(tail)
                if ext == '.wav':
                    Sounds.sounds[name] = pygame.mixer.Sound(os.path.join(root, f))
        # self.shell_fired = pygame.mixer.Sound("sounds/ShellFired.wav")
        # self.missile_fired = pygame.mixer.Sound("sounds/MissileFired.wav")
        # self.explosion = pygame.mixer.Sound("sounds/ExpFort.wav")
        # self.collision = pygame.mixer.Sound("sounds/Collision.wav")
        # self.vlner_reset = pygame.mixer.Sound("sounds/VulnerZeroed.wav")
        # self.beep_high = pygame.mixer.Sound("sounds/beep-high.wav")
        # self.beep_low = pygame.mixer.Sound("sounds/beep-low.wav")
        # self.warn_high = pygame.mixer.Sound("sounds/warn-high.wav")
        # self.warn_low = pygame.mixer.Sound("sounds/warn-low.wav")

    @staticmethod
    def play(sound_id):
        if sound_id in Sounds.sounds:
            Sounds.sounds[sound_id].play()
        else:
            raise Exception('Unable to play sound "%s"'%sound_id)