import pygame
import neat
import time
import os
import random
from pygame.sprite import Sprite, Group
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT
)

'''
PAC MAN:
3 lives
dots -- all dots eaten? proceed tp next level
pacman
ghosts -- color : Red, Pink, Cyan, Orange -- All 
    - pm loses one life when comes in contact
energizers
'''
pygame.init()

# Game screen size
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

# Global vars
DIRECTIONS = [-1, 1, -2, 2]
ghosts_vulnerable = False
dots_remaining = 1
SPEED_NORMAL_PAC = 20


# Define game objects
class PacMan(Sprite):
    def __init__(self):
        super(PacMan, self).__init__()
        # surf is used to control the graphical representation of pac man
        # self.surf = pygame.Surface((75, 25))
        # self.surf.fill((255, 255, 255))
        img = pygame.image.load('pacman.png').convert_alpha()
        img = pygame.transform.scale(img, (50, 50))
        self.surf = img
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # rect is the underlying rectangle for surf -- used to control the position
        self.rect = self.surf.get_rect()
        # speed is the number of pixels moved in one frame
        self.speed = SPEED_NORMAL_PAC
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

    def move(self, obstacle_in_front=False):
        if obstacle_in_front:
            speed = 0
            return
        else:
            self.speed = SPEED_NORMAL_PAC

        steps_y = 0 if abs(self.direction) == 2 else self.speed * self.direction
        steps_x = 0 if abs(self.direction) == 1 else self.speed * self.direction / 2
        # Prevent going out of screen
        if self.rect.right + steps_x > SCREEN_WIDTH:
            steps_x = SCREEN_WIDTH - self.rect.right
            self.speed = 0
        elif self.rect.left + steps_x < 0:
            steps_x = -self.rect.left
            self.speed = 0
        if self.rect.bottom + steps_y > SCREEN_HEIGHT:
            steps_y = SCREEN_HEIGHT - self.rect.bottom
            self.speed = 0
        elif self.rect.top + steps_y < 0:
            steps_y = -self.rect.top
            self.speed = 0

        # Move it!
        self.rect = self.rect.move(steps_x, steps_y)


class Ghost(Sprite):
    def __init__(self, img_loc):
        super(Ghost, self).__init__()
        self.img_path = img_loc
        img = pygame.image.load(img_loc)
        img = pygame.transform.scale(img, (40, 40))
        self.surf = img.convert()
        # https://www.kite.com/python/docs/pygame.Surface.set_colorkey
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.surf.set_alpha(255)
        self.rect = self.surf.get_rect(center=(100, 100))
        self.direction = 2
        self.speed = random.randint(5, 20)
        self.infected_last = None

    def pick_another_direction(self):
        current_dir = self.direction
        possible_dirs = [d for d in DIRECTIONS if d != current_dir]
        new_dir_ind = random.randint(0, len(possible_dirs) - 1)
        self.direction = possible_dirs[new_dir_ind]

    def move(self, obstacle_in_front=False):
        if obstacle_in_front:
            self.pick_another_direction()
            return

        steps_y = 0 if abs(self.direction) == 2 else self.speed * self.direction
        steps_x = 0 if abs(self.direction) == 1 else self.speed * self.direction / 2
        # Prevent going out of screen
        if self.rect.right + steps_x > SCREEN_WIDTH:
            steps_x = SCREEN_WIDTH - self.rect.right
            self.pick_another_direction()
        elif self.rect.left + steps_x < 0:
            steps_x = -self.rect.left
            self.pick_another_direction()
        if self.rect.bottom + steps_y > SCREEN_HEIGHT:
            steps_y = SCREEN_HEIGHT - self.rect.bottom
            self.pick_another_direction()
        elif self.rect.top + steps_y < 0:
            steps_y = -self.rect.top
            self.pick_another_direction()

        # Move it!
        self.rect.move_ip(steps_x, steps_y)

    def run_for_life(self):
        self.speed *= 5
        self.infected_last = pygame.time.get_ticks()

    def become_normal(self):
        if self.infected_last and (pygame.time.get_ticks() - self.infected_last) >= 25000:
            self.speed /= 5
            self.infected_last = None


class Energizer(Sprite):
    def __init__(self, pos):
        super(Energizer, self).__init__()
        self.surf = pygame.Surface((20, 20))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(center=pos)


class Dot(Sprite):
    def __init__(self, pos):
        super(Dot, self).__init__()
        self.surf = pygame.Surface((2, 2))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(center=pos)


# Initialize the display screen
screen_surface = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

running = True
pac = PacMan()
ghost = Ghost('ghost1.png')
enemies = Group()
enemies.add(ghost)
IMG_WIDTH = 50
IMG_HEIGHT = 50
e = Energizer((SCREEN_WIDTH - IMG_WIDTH / 2, SCREEN_HEIGHT - IMG_HEIGHT / 2))
energizers = Group()
energizers.add(e)
all_sprites = Group()

MARGIN = IMG_WIDTH // 2
NUM_X = (SCREEN_WIDTH - MARGIN) // (2 + MARGIN)
NUM_Y = (SCREEN_HEIGHT - MARGIN) // (2 + MARGIN)
dots_remaining = NUM_X * NUM_Y
dots = Group()
for x in range(NUM_X):
    for y in range(NUM_Y):
        DOT_WIDTH = 2
        DOT_HEIGHT = 2
        dot = Dot(((MARGIN + DOT_WIDTH) * x + MARGIN, (MARGIN + DOT_HEIGHT) * y + MARGIN))
        dots.add(dot)
        all_sprites.add(dot)

all_sprites.add(pac, ghost, e)

# game clock
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen_surface.fill((0, 0, 0))
    for ghost in enemies:
        ghost.become_normal()
    pac.change_direction(pygame.key.get_pressed())

    pac.move()
    for ghost in enemies:
        ghost.move()
    # copy the contents from another_surface to screen_surface
    for entity in all_sprites:
        screen_surface.blit(entity.surf, entity.rect)

    # check for collisions between pacman and enemies
    ghost_collided = pygame.sprite.spritecollideany(pac, enemies)
    if ghost_collided:
        if ghosts_vulnerable:
            img_path = ghost_collided.img_path
            ghost_collided.kill()
            # respawn
            new_ghost = Ghost(img_path)
            enemies.add(new_ghost)
            all_sprites.add(new_ghost)
        else:
            pac.kill()
            running = False

    # check if pacman consumes a energizer
    energizer_consumed = pygame.sprite.spritecollideany(pac, energizers)
    if energizer_consumed:
        ghosts_vulnerable = True
        energizer_consumed.kill()
        for ghost in enemies:
            ghost.run_for_life()

    # check if pacman consumes a dot
    dots_consumed = pygame.sprite.spritecollideany(pac, dots)
    if dots_consumed:
        dots_consumed.kill()
        dots_remaining -= 1
    print(dots_remaining)
    if dots_remaining == 0:
        print('Game over!')
        running = False

    # now pour contents of screen_surface to user display
    pygame.display.flip()

    # Number of frames per second
    clock.tick(2.5)

pygame.quit()
