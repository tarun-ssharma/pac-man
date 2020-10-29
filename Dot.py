import pygame
from pygame.sprite import Sprite


class Dot(Sprite):
    def __init__(self, pos):
        super(Dot, self).__init__()
        self.pos = pos
        self.surf = pygame.Surface((1, 1))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(center=pos)
        self.exists = True

    def eaten(self):
        self.exists = False
