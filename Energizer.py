import pygame
from pygame.sprite import Sprite


class Energizer(Sprite):
    def __init__(self, pos):
        super(Energizer, self).__init__()
        self.surf = pygame.Surface((5, 5))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(center=pos)
        self.exists = True

    def eaten(self):
        self.exists = False
