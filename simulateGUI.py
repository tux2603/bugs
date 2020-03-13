import pyglet
from pyglet.sprite import Sprite
from pyglet.window import key
import threading
import neat
import random
from time import sleep, time
from math import atan2, sqrt
import numpy as np
from bugs import Bug

NUM_BUGS = 50

GEN_TIME = 300
genStart = 0

BUG_MAX_SPEED = 12
BUG_TURN_RATE = 4

# The amount of space to put between the edge of the screen and spawned-in bugs
BUG_BUFFER = 32

Bug.visionRange = (-60, 60)

Bug.massPerFood = 0.001
Bug.mass = 0.01
Bug.velocityScaling = 0.1
Bug.baseStarvation = 0.01
Bug.startingHunger = STARTING_HUNGER = 3

NUM_FOODS = 20

genNum = 0
speedModifier = 1

##############################################################################
##########                       PYGLET STUFF                       ##########
##############################################################################
Bug.worldWidth = SCREEN_WIDTH = 1500
Bug.worldHeight = SCREEN_HEIGHT = 1000

generationLock = threading.Lock()

gameWindow = pyglet.window.Window(
    width=SCREEN_WIDTH, height=SCREEN_HEIGHT, fullscreen=False)

# Set the window background color
pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)

keyboard = key.KeyStateHandler()
oldKeyboard = key.KeyStateHandler()
gameWindow.push_handlers(keyboard)

# Initialize game variables and stuff
fpsDisplay = pyglet.window.FPSDisplay(window=gameWindow)

backgroundBatch = pyglet.graphics.Batch()
foodBatch = pyglet.graphics.Batch()
bugsBatch = pyglet.graphics.Batch()
hudBatch = pyglet.graphics.Batch()


pyglet.resource.path = ['resources']
pyglet.resource.reindex()

uglyBug = pyglet.resource.image('images/uglyBug.png')
uglyBug.anchor_x = uglyBug.width / 2
uglyBug.anchor_y = uglyBug.height / 2

yummyCookie = pyglet.resource.image('images/yummyCookie.png')
yummyCookie.anchor_x = yummyCookie.width / 2
yummyCookie.anchor_y = yummyCookie.height / 2

chocolateChip = pyglet.resource.image('images/yummyChocolate.png')
chocolateChip.anchor_x = chocolateChip.width / 2
chocolateChip.anchor_y = chocolateChip.height / 2

bugInfoLabel = pyglet.text.Label('Hello, world',
                                 font_name=None,
                                 color=(0, 0, 0, 100),
                                 font_size=20,
                                 x=5, y=SCREEN_HEIGHT - 5,
                                 anchor_x='left', anchor_y='top')


bugSprites = []
foods = []
bugsAlive = 0

for i in range(NUM_FOODS):
    chip = Sprite(chocolateChip, batch=foodBatch, x=random.randint(
        0, SCREEN_WIDTH), y=random.randint(0, SCREEN_HEIGHT))
    foods.append(chip)

@gameWindow.event
def on_draw():
    gameWindow.clear()
    backgroundBatch.draw()
    foodBatch.draw()
    bugsBatch.draw()
    hudBatch.draw()
    bugInfoLabel.draw()
    fpsDisplay.draw()

    # TEST_BUG.draw()


def update(dt):
    global bugsAlive, bugSprites, oldKeyboard, genStart, foods, speedModifier

    if (time() - genStart) * int(speedModifier) >= GEN_TIME:
        print("KILLING ALL BUGS")
        genStart = time()
        for bug in bugSprites:
            bug.visible = False
        bugsAlive = 0
        print("There are now {} bugs alive".format(bugsAlive))

    if keyboard[key.PLUS] or keyboard[key.EQUAL]:
        speedModifier *= 1.01

    elif keyboard[key.MINUS] or keyboard[key.UNDERSCORE]:
        speedModifier /= 1.01
        if speedModifier < 1:
            speedModifier = 1

    if not generationLock.locked():
        bugInfoLabel.text = "Generation {} - {} seconds - {} bugs alive - SPEED {}x".format(
            genNum, int((time() - genStart) * int(speedModifier)), bugsAlive, int(speedModifier))
        with generationLock:
            bugCount = 0
            bugsStillAlive = False
            for i in range(int(speedModifier)):
                for bug in bugSprites:
                    if bug.visible:
                        bugCount += 1
                        bugsStillAlive = True
                        bug.useBrain(foods)

            if not bugsStillAlive:
                bugsAlive = 0
            else:
                bugsAlive = bugCount // int(speedModifier)


##############################################################################
##########                        NEAT STUFF                        ##########
##############################################################################


# Load configuration.
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config')

# Create the population, which is the top-level object for a NEAT run.
p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)


def trainingThread():
    winner = p.run(evalBugs)


def evalBugs(genomes, config):
    global uglyBug, bugsBatch, bugSprites, bugsAlive, genStart, genNum

    with generationLock:

        i = 0
        for genomeID, genome in genomes:
            bug = bugSprites[i]
            bug.position = (random.randint(BUG_BUFFER, SCREEN_WIDTH - BUG_BUFFER), random.randint(0, SCREEN_HEIGHT - BUG_BUFFER))
            bug.rotation = random.randint(0, 360)
            bug.visible = True
            genome.fitness = 0
            bug.brain = neat.nn.FeedForwardNetwork.create(genome, config)
            bug.fitness = 0
            bug.hunger = STARTING_HUNGER
            bug.genome = genome
            bug.genomeID = genomeID
            i += 1

        bugsAlive = len(genomes)

        genStart = time()

    while bugsAlive > 1:
        sleep(0.1)

    print("##### THE BUGS DIED #####")
    genNum += 1

    for bug in bugSprites:
        if bug.genome is not None:
            bug.genome.fitness = bug.fitness

##############################################################################
##########                        GAME STUFF                        ##########
##############################################################################


if __name__ == '__main__':

    for i in range(NUM_BUGS):
        bug = Bug(uglyBug, batch=bugsBatch)
        bug.visible = False
        bugSprites.append(bug)
        bug.maxSpeed = 100

    # Create the generational training thread
    trainingThread = threading.Thread(target=trainingThread)

    trainingThread.start()

    pyglet.clock.schedule_interval(update, 1/240.0)

    pyglet.app.run()
