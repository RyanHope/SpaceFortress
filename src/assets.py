import pygame

class Assets(object):
    def __init__(self):
        pass
    @staticmethod
    def load():
        Assets.f = pygame.font.Font("fonts/freesansbold.ttf", 14)
        Assets.f24 = pygame.font.Font("fonts/freesansbold.ttf", 20)
        Assets.f28 = pygame.font.Font("fonts/freesansbold.ttf", 28)
        Assets.f96 = pygame.font.Font("fonts/freesansbold.ttf", 72)
        Assets.f36 = pygame.font.Font("fonts/freesansbold.ttf", 36)
        Assets.vector_explosion = pygame.image.load("gfx/exp.png")
        Assets.vector_explosion.set_colorkey((0, 0, 0))
        Assets.vector_explosion_rect = Assets.vector_explosion.get_rect()
