import pyglet
from pyglet.sprite import Sprite
from pyglet.window import key
import threading
import neat
import visualize
import random
from time import sleep, time
from math import atan2, sqrt
import numpy as np
from bugs import HeadlessBug as Bug

GEN_TIME = 300
genStart = 0

Bug.maxSpeed = 16
Bug.turnRate = 4

# The amount of space to put between the edge of the screen and spawned-in bugs
BUG_BUFFER = 32

Bug.visionRange = (-60, 60)

Bug.massPerFood = 0.001
Bug.mass = 0.01
Bug.velocityScaling = 0.1
Bug.baseStarvation = 0.01
Bug.startingHunger = STARTING_HUNGER = 3

Bug.worldHeight = WORLD_HEIGHT = 1000
Bug.worldWidth = WORLD_WIDTH = 1500
NUM_FOODS = 20

genNum = 0
speedModifier = 1

def evalBugs(genome, config):

    bugs = []

    # for genomeID, genome in genomes:
    bug = Bug()
    bug.position = (random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT))
    bug.rotation = random.randint(0, 360)
    bug.isAlive = True
    genome.fitness = 0
    bug.brain = neat.nn.FeedForwardNetwork.create(genome, config)
    bug.fitness = 0
    bug.hunger = STARTING_HUNGER
    bug.genome = genome
    # bug.genomeID = genomeID
    bugs.append(bug)

    bugAlive = True

    updatesLeft = 108000

    foods = []

    for i in range(NUM_FOODS):
        chip = (random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT))
        foods.append(chip)

    while bugAlive and updatesLeft > 0:
        bugAlive = False
        # for bug in bugs:
        if bug.isAlive:
            bugAlive = True
            bug.useBrain(foods)
        updatesLeft -= 1
                    
    # genNum += 1

    # sleep(1)
    return bug.fitness

##############################################################################
##########                        GAME STUFF                        ##########
##############################################################################


if __name__ == '__main__':
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        'config')

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    te = neat.ParallelEvaluator(64, evalBugs)
    winner = p.run(te.evaluate, 100)
    
    nodeNames = {-1: 'Direction', -2: 'Distance', -3: 'Hunger', -4: 'Bias', 0: 'Rotation Bias 1', 1: 'Rotation Bias 2', 2: 'Speed Bias 1', 3: 'Speed Bias 2'}
    visualize.draw_net(config, winner, True, node_names=nodeNames)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

