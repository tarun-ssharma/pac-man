import os
import random
import time
from Dot import Dot
from Energizer import Energizer
from Ghost import Ghost
from PacMan import PacMan
import neat
import pygame
import pickle
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
from pygame.sprite import Sprite, Group

SCREEN_WIDTH = 100
SCREEN_HEIGHT = 100
DIRECTIONS = [-1, 1, -2, 2]
IMG_WIDTH = 10
IMG_HEIGHT = 10
SPEED_NORMAL_PAC = IMG_WIDTH

# Different for each genome
ghosts_vulnerable = False
enemies = None
energizers = None
dots = None
all_sprites = None
screen_surface = None
pac = None
dots_remaining = None
clock = None
p = None
stats = None


def reset_global():
    global ghosts_vulnerable, enemies, energizers, dots, all_sprites, screen_surface, pac, dots_remaining, clock, p, stats
    ghosts_vulnerable = False
    enemies = None
    energizers = None
    dots = None
    all_sprites = None
    screen_surface = None
    pac = None
    dots_remaining = None
    clock = None
    p = None
    stats = None


def game_loop(genomes, config, draw=False):
    global enemies, ghosts_vulnerable, pac, dots_remaining, screen_surface, all_sprites, dots, clock, energizers
    for genome_id, genome in genomes:
        # For each genome, we average out the fitness over 10 simulations
        # Trying to average out over ghost's randomness
        ctr = 10
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        cumulative_fitness = 0
        while (ctr):
            ctr -= 1
            reset_global()
            initialize_pygame()
            running = True
            num_moves = 150
            while running:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                        break

                if draw:
                    screen_surface.fill((0, 0, 0))
                for enemy in enemies:
                    if enemy.become_normal():
                        ghosts_vulnerable = False

                # user operated -- pac.change_direction(pygame.key.get_pressed())
                # TODO: ADjust for multiple enemies
                ghost = list(enemies)[0]
                energizer = list(energizers)[0]
                inp = [pac.rect.top, pac.rect.bottom, pac.rect.left, pac.rect.right, pac.speed, pac.direction,
                       ghost.rect.top, ghost.rect.bottom, ghost.rect.left, ghost.rect.right, ghost.speed,
                       ghost.direction, ghosts_vulnerable]
                for dot in dots:
                    if dot.exists:
                        inp.append(1)
                    else:
                        inp.append(0)

                for energizer in energizers:
                    if energizer.exists:
                        inp.append(1)
                    else:
                        inp.append(0)

                output = net.activate(inp)
                if output[0] > 0.5:
                    pac.change_direction({K_UP: True, K_DOWN: False, K_LEFT: False, K_RIGHT: False})
                elif output[1] > 0.5:
                    pac.change_direction({K_DOWN: True, K_UP: False, K_LEFT: False, K_RIGHT: False})
                elif output[2] > 0.5:
                    pac.change_direction({K_LEFT: True, K_DOWN: False, K_UP: False, K_RIGHT: False})
                elif output[3] > 0.5:
                    pac.change_direction({K_RIGHT: True, K_DOWN: False, K_UP: False, K_LEFT: False})
                # NN output operated --
                pac.move(SCREEN_WIDTH, SCREEN_HEIGHT)
                for enemy in enemies:
                    enemy.move(SCREEN_WIDTH, SCREEN_HEIGHT, DIRECTIONS)

                if draw:
                    for entity in dots:
                        if entity.exists:
                            screen_surface.blit(entity.surf, entity.rect)

                    for entity in energizers:
                        if entity.exists:
                            screen_surface.blit(entity.surf, entity.rect)

                    for entity in enemies:
                        screen_surface.blit(entity.surf, entity.rect)

                    screen_surface.blit(pac.surf, pac.rect)

                # check for collisions between pacman and enemies
                ghost_collided = pygame.sprite.spritecollideany(pac, enemies)
                if ghost_collided:
                    if ghosts_vulnerable and ghost_collided.infected_last:
                        img_path = ghost_collided.img_path
                        ghost_collided.kill()
                        # respawn
                        new_ghost = Ghost(img_path, SPEED_NORMAL_PAC)
                        enemies.add(new_ghost)
                        all_sprites.add(new_ghost)
                    else:
                        pac.kill()
                        running = False
                        break

                # check if pacman consumes a energizer
                energizer_consumed = pygame.sprite.spritecollideany(pac, energizers)
                if energizer_consumed and energizer_consumed.exists:
                    ghosts_vulnerable = True
                    energizer_consumed.eaten()
                    for enemy in enemies:
                        enemy.run_for_life()

                # check if pacman consumes a dot
                dots_consumed = pygame.sprite.spritecollideany(pac, dots)
                if dots_consumed and dots_consumed.exists:
                    dots_consumed.eaten()
                    dots_remaining -= 1
                    cumulative_fitness += 1

                if dots_remaining == 0:
                    running = False
                    break

                num_moves -= 1
                if num_moves == 0:
                    running = False
                    break

                # now pour contents of screen_surface to user display
                if draw:
                    pygame.display.flip()

                # Number of frames per second
                clock.tick(500)

            pygame.quit()
        genome.fitness = cumulative_fitness / 10
        print(genome.fitness)


def initialize_neat():
    global p, stats
    config_file = os.path.join(os.getcwd(), 'neat_config.ini')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    # Initial population
    p = neat.Population(config)

    # Add reporters
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))


def show_results():
    pass


def initialize_pygame():
    global enemies, ghosts_vulnerable, pac, dots_remaining, screen_surface, all_sprites, dots, clock, energizers

    pygame.init()

    enemies = Group()
    energizers = Group()
    dots = Group()
    all_sprites = Group()

    # Initialize the display screen
    screen_surface = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

    # Add a pac man
    pac = PacMan(SPEED_NORMAL_PAC)

    # Add ghosts
    ghost = Ghost('ghost1.png', SPEED_NORMAL_PAC)

    # Create a ghosts group
    enemies.add(ghost)

    # Create energizers and their group
    e = Energizer((SCREEN_WIDTH - IMG_WIDTH / 2, SCREEN_HEIGHT - IMG_HEIGHT / 2))
    energizers.add(e)

    # Create dots and add them to a group
    margin = IMG_WIDTH
    num_x = (SCREEN_WIDTH) // (margin)
    num_y = (SCREEN_HEIGHT) // (margin)
    dots_remaining = num_x * num_y
    dot_width = 1
    dot_height = 1
    for x in range(num_x):
        for y in range(num_y):
            dot = Dot((margin * x + margin / 2 - dot_width / 2, margin * y + margin / 2 - dot_height / 2))
            dots.add(dot)
            all_sprites.add(dot)

    all_sprites.add(pac, ghost, e)

    # game clock
    clock = pygame.time.Clock()


def main():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    initialize_neat()

    # Run for 300 generations
    winner_genome = p.run(game_loop, 100)
    print(f'Best genome:{winner_genome}')
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner_genome, f)
    # pickle the winner
    # later take it out and simulate without headless

# def main():
#     global p
#     initialize_neat()
#     config_file = os.path.join(os.getcwd(), 'neat_config.ini')
#     config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation,
#                          config_file)
#     with open('winner.pkl','rb') as f:
#         g = pickle.load(f)
#     genomes = [('id',g)]
#     game_loop(genomes=genomes, config=config, draw=True)


if __name__ == '__main__':
    main()
