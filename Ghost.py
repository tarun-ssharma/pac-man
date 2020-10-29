import pygame
from pygame.sprite import Sprite
from pygame.locals import RLEACCEL
import random


class Ghost(Sprite):
    def __init__(self, img_loc, speed):
        super(Ghost, self).__init__()
        self.img_path = img_loc
        img = pygame.image.load(img_loc)
        img = pygame.transform.scale(img, (10, 10))
        self.surf = img.convert()
        # https://www.kite.com/python/docs/pygame.Surface.set_colorkey
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.surf.set_alpha(255)
        self.rect = self.surf.get_rect(center=(40, 40))
        self.direction = 2
        self.speed = speed
        self.infected_last = None

    def pick_another_direction(self, dirs):
        current_dir = self.direction
        possible_dirs = [d for d in dirs if d != current_dir]
        new_dir_ind = random.randint(0, len(possible_dirs) - 1)
        self.direction = possible_dirs[new_dir_ind]

    def move(self, screen_width, screen_height, dirs, obstacle_in_front=False):
        if obstacle_in_front:
            self.pick_another_direction()
            return

        steps_y = 0 if abs(self.direction) == 2 else self.speed * self.direction
        steps_x = 0 if abs(self.direction) == 1 else self.speed * self.direction / 2
        # Prevent going out of screen
        if self.rect.right + steps_x > screen_width:
            steps_x = screen_width - self.rect.right
            self.pick_another_direction(dirs)
        elif self.rect.left + steps_x < 0:
            steps_x = -self.rect.left
            self.pick_another_direction(dirs)
        if self.rect.bottom + steps_y > screen_height:
            steps_y = screen_height - self.rect.bottom
            self.pick_another_direction(dirs)
        elif self.rect.top + steps_y < 0:
            steps_y = -self.rect.top
            self.pick_another_direction(dirs)

        # Move it!
        self.rect.move_ip(steps_x, steps_y)

    def run_for_life(self):
        self.speed /= 2
        self.infected_last = pygame.time.get_ticks()

    def become_normal(self):
        if self.infected_last and (pygame.time.get_ticks() - self.infected_last) >= 25000:
            self.speed *= 2
            self.infected_last = None
            return True
        return False
