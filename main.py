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
Load images
'''

'''
PAC MAN:
3 lives
dots -- all dots eaten? proceed tp next level
pacman
ghosts -- color : Red, Pink, Cyan, Orange -- All 
    - pm loses one life when comes in contact
energizers
'''

'''
1. Exploring pygame
'''
pygame.init()

# Game screen size
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

# Global vars
DIRECTIONS = [-1, 1, -2, 2]
ghosts_vulnerable = False


# Define game objects
class PacMan(Sprite):
    def __init__(self):
        super(PacMan, self).__init__()
        # surf is used to control the graphical representation of pac man
        # self.surf = pygame.Surface((75, 25))
        # self.surf.fill((255, 255, 255))
        img = pygame.image.load('pacman.png').convert_alpha()
        self.img = pygame.transform.scale(img, (50, 50))
        self.surf = self.img
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # rect is the underlying rectangle for surf -- used to control the position
        self.rect = self.surf.get_rect()
        # speed is the number of pixels moved in one frame
        self.speed = 2
        self.direction = 2

    '''
    1 = up, 2 = down, 3= left, 4= right
    '''
    def change_direction(self, pressed_keys):
        if pressed_keys[K_UP]:
            # TODO: Issue here: image moves back to top left from wherever
            center_ = self.surf.get_rect().center
            self.surf = pygame.transform.rotate(self.img, 90)
            self.rect = self.surf.get_rect()
            new_center = self.rect
            new_center.center = center_
            self.direction = -1
        elif pressed_keys[K_DOWN]:
            self.direction = 1
        elif pressed_keys[K_LEFT]:
            self.direction = -2
        elif pressed_keys[K_RIGHT]:
            self.direction = 2

    def move(self, obstacle_in_front=False):
        if obstacle_in_front:
            speed = 0
            return
        else:
            self.speed = 2

        steps_y = 0 if abs(self.direction) == 2 else self.speed*self.direction
        steps_x = 0 if abs(self.direction) == 1 else self.speed*self.direction/2
        # Prevent going out of screen
        if self.rect.right + steps_x > SCREEN_WIDTH:
            steps_x = SCREEN_WIDTH - self.rect.right
            self.speed = 0
        elif self.rect.left + steps_x < 0:
            steps_x = -self.rect.left
            self.speed = 0
        if self.rect.bottom + steps_x > SCREEN_HEIGHT:
            steps_y = SCREEN_HEIGHT - self.rect.bottom
            self.speed =0
        elif self.rect.top + steps_y < 0:
            steps_y = -self.rect.top
            self.speed = 0

        # Move it!
        self.rect.move_ip(steps_x, steps_y)


class Ghost(Sprite):
    def __init__(self, img_path):
        super(Ghost, self).__init__()
        self.img_path = img_path
        img = pygame.image.load(img_path)
        img = pygame.transform.scale(img, (50, 50))
        self.surf = img.convert()
        # https://www.kite.com/python/docs/pygame.Surface.set_colorkey
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=(100, 100))
        self.direction = 2
        self.speed = random.randint(5, 20)

    def kill(self):
        img_path = self.img_path
        self.kill()
        # respawn
        new_ghost = Ghost(img_path)
        enemies.add(new_ghost)
        all_sprites.add(new_ghost)
        return new_ghost

    def pick_another_direction(self):
        current_dir = self.direction
        possible_dirs = [d for d in DIRECTIONS if d != current_dir]
        new_dir_ind = random.randint(0, len(possible_dirs)-1)
        self.direction = possible_dirs[new_dir_ind]

    def move(self, obstacle_in_front=False):
        if obstacle_in_front:
            self.pick_another_direction()
            return

        steps_y = 0 if abs(self.direction) == 2 else self.speed*self.direction
        steps_x = 0 if abs(self.direction) == 1 else self.speed*self.direction/2
        # Prevent going out of screen
        if self.rect.right + steps_x > SCREEN_WIDTH:
            steps_x = SCREEN_WIDTH - self.rect.right
            self.pick_another_direction()
        elif self.rect.left + steps_x < 0:
            steps_x = -self.rect.left
            self.pick_another_direction()
        if self.rect.bottom + steps_x > SCREEN_HEIGHT:
            steps_y = SCREEN_HEIGHT - self.rect.bottom
            self.pick_another_direction()
        elif self.rect.top + steps_y < 0:
            steps_y = -self.rect.top
            self.pick_another_direction()

        # Move it!
        self.rect.move_ip(steps_x, steps_y)


class Energizer(Sprite):
    def __init__(self, pos):
        super(Energizer, self).__init__()
        self.surf = pygame.Surface((20, 20))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(center=pos)


# Initialize the display screen
screen_surface = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

running = True
pac = PacMan()
ghost = Ghost('ghost1.png')
enemies = Group()
enemies.add(ghost)
e = Energizer((SCREEN_WIDTH, SCREEN_HEIGHT))
energizers = Group()
energizers.add(e)
all_sprites = Group()
all_sprites.add(pac, ghost, e)

# custom event
ADDGHOST = pygame.USEREVENT + 1
# control in what intervals this event fires
pygame.time.set_timer(ADDGHOST, 250)

# game clock
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen_surface.fill((0, 0, 0))
    pac.change_direction(pygame.key.get_pressed())
    pac.move()
    ghost.move()
    # copy the contents from another_surface to screen_surface
    for entity in all_sprites:
        screen_surface.blit(entity.surf, entity.rect)

    # check for collisions
    ghost_collided = pygame.sprite.spritecollideany(pac, enemies)
    if ghost_collided:
        if ghosts_vulnerable:
            ghost_collided.kill()
        else:
            print('DIE!')
            pac.kill()
            running = False

    # now pour contents of screen_surface to user display
    pygame.display.flip()

    clock.tick(2)

pygame.quit()

# TODO : https://realpython.com/pygame-a-primer/#collision-detection
