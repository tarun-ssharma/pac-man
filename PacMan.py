import pygame
from pygame.sprite import Sprite
from pygame.locals import RLEACCEL, K_UP, K_DOWN, K_RIGHT, K_LEFT


class PacMan(Sprite):
    def __init__(self, speed):
        super(PacMan, self).__init__()
        # surf is used to control the graphical representation of pac man
        # self.surf = pygame.Surface((75, 25))
        # self.surf.fill((255, 255, 255))
        img = pygame.image.load('pacman.png').convert_alpha()
        img = pygame.transform.scale(img, (10, 10))
        self.surf = img
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # rect is the underlying rectangle for surf -- used to control the position
        self.rect = self.surf.get_rect()
        # speed is the number of pixels moved in one frame
        self.initial_speed = speed
        self.speed = speed
        self.direction = 2

    '''
    -1 = up, 1 = down, -2= left, 2= right
    rotation happens anti-clockwise
    '''

    def change_direction(self, pressed_keys):
        if pressed_keys[K_UP]:
            # TODO: Issue here: image moves back to top left from wherever
            if self.direction != -1:
                angle = 180 if self.direction == 1 else (270 if self.direction == -2 else 90)
                self.surf = pygame.transform.rotate(self.surf, angle)
                self.direction = -1
        elif pressed_keys[K_DOWN]:
            if self.direction != 1:
                angle = 180 if self.direction == -1 else (90 if self.direction == -2 else 270)
                self.surf = pygame.transform.rotate(self.surf, angle)
                self.direction = 1
        elif pressed_keys[K_LEFT]:
            if self.direction != -2:
                angle = 90 if self.direction == -1 else (180 if self.direction == 2 else 270)
                self.surf = pygame.transform.rotate(self.surf, angle)
                self.direction = -2
        elif pressed_keys[K_RIGHT]:
            if self.direction != 2:
                angle = 270 if self.direction == -1 else (180 if self.direction == -2 else 90)
                self.surf = pygame.transform.rotate(self.surf, angle)
                self.direction = 2

    def move(self, screen_width, screen_height, obstacle_in_front=False):
        if obstacle_in_front:
            self.speed = 0
            return
        else:
            self.speed = self.initial_speed

        steps_y = 0 if abs(self.direction) == 2 else self.speed * self.direction
        steps_x = 0 if abs(self.direction) == 1 else self.speed * self.direction / 2
        # Prevent going out of screen
        if self.rect.right + steps_x > screen_width:
            steps_x = screen_width - self.rect.right
            self.speed = 0
        elif self.rect.left + steps_x < 0:
            steps_x = -self.rect.left
            self.speed = 0
        if self.rect.bottom + steps_y > screen_height:
            steps_y = screen_height - self.rect.bottom
            self.speed = 0
        elif self.rect.top + steps_y < 0:
            steps_y = -self.rect.top
            self.speed = 0

        # Move it!
        self.rect = self.rect.move(steps_x, steps_y)
