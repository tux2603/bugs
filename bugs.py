import pyglet
from SpriteLibraries import Sprite
from pyglet.window import key
import threading
import neat
import random
from time import sleep
from math import atan2, sqrt
import numpy as np
from time import time

NUM_BUGS = 50

GEN_TIME = 300
genStart = 0

BUG_MAX_SPEED = 12
BUG_TURN_RATE = 4

# The amount of space to put between the edge of the screen and spawned-in bugs
BUG_BUFFER = 32

BUG_VISION_RANGE = (-60, 60)

MASS_PER_FOOD = 0.001
BUG_MASS = 0.01
VELOCITY_FACTOR = 0.1
BASE_SARTVATION = 0.01
STARTING_HUNGER = 3

NUM_FOODS = 20

genNum = 0
speedModifier = 1

##############################################################################
##########                         THE BUGS                         ##########
##############################################################################


class Bug(Sprite):
    def __init__(self, img, x=0, y=0, blend_src=770, blend_dest=771, batch=None, group=None, usage='dynamic', subpixel=False):
        super(Bug, self).__init__(img, x=x, y=y, blend_src=blend_src, blend_dest=blend_dest,
                                  batch=batch, group=group, usage=usage, subpixel=subpixel)
        self.hunger = 0
        self.fitness = 0
        self.brain = None
        self.genome = None
        self.genomeID = None

    def useBrain(self, foodSprites):
        global bugsAlive
        leftEyeChipDistances = [0, 0, 0]
        rightEyeChipDistances = [0, 0, 0]

        minChipDistance = 10000000
        minChipDirection = 0

        for chip in foodSprites:
            chipDirection = headingBetween(
                self.position, chip.position) - self.rotation
            chipDirection %= 360
            chipDirection + 360
            chipDirection %= 360

            if chipDirection > 180:
                chipDirection -= 360
            elif chipDirection < -180:
                chipDirection += 360

            chipDistance = distanceBetween(
                self.position, chip.position)

            if chipDirection >= BUG_VISION_RANGE[0] and chipDirection <= BUG_VISION_RANGE[1] and chipDistance < minChipDistance:
                minChipDistance = chipDistance
                minChipDirection = chipDirection

            if chipDistance < 16:
                self.fitness += 1
                self.hunger += 1
                # print("\tBug now has {} food in its belly".format(bugHungers[i]))
                chip.position = (random.randint(
                    0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))

        # print("{}: {} {} {}".format(i, chipDirection, leftEyeChipDistances, rightEyeChipDistances))

        # TODO Change any of this stuff to your hearts content! Make the bugs smart
        adjustedDirection = minChipDirection / (BUG_VISION_RANGE[1] - BUG_VISION_RANGE[0])
        adjustedDistance = minChipDistance
        hungerLevel = 1 / self.hunger if self.hunger != 0 else 100000000

        inputs = (adjustedDirection, adjustedDistance, hungerLevel, 1.0)

        output = self.brain.activate(inputs) if self.brain is not None else (0, 0, 0, 0)

        self.changeDirectionAngle(
            (output[0] - output[1]) * BUG_TURN_RATE)
        self.rotation += (output[0] - output[1]) * BUG_TURN_RATE
        self.setSpeed(abs(output[2] - output[3]) * BUG_MAX_SPEED)
        self.move()

        self.position = (max(min(self.position[0], SCREEN_WIDTH), 0), max(
            min(self.position[1], SCREEN_HEIGHT), 0))

        self.hunger -= BASE_SARTVATION + 0.5 * (BUG_MASS + self.hunger * MASS_PER_FOOD) * self.getSpeed() * self.getSpeed() * VELOCITY_FACTOR * VELOCITY_FACTOR

        if self.hunger < 0:
            # print("!!!!! Bug {} starved to death :( !!!!!".format(i))
            # print("\tIt had {} food in its belly".format(bugHungers[i]))
            self.visible = False
            bugsAlive -= 1


##############################################################################
##########                       PYGLET STUFF                       ##########
##############################################################################
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1000

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


# TEST_BUG = Sprite(uglyBug, x=SCREEN_WIDTH/2, y=SCREEN_HEIGHT/2)
# TEST_BUG.setSpeedAndDirection(1, 45)

bugSprites = []
# bugBrains = []
# bugFitnesses = []
# bugHungers = []
foods = []
bugsAlive = 0

for i in range(NUM_FOODS):
    chip = Sprite(chocolateChip, batch=foodBatch, x=random.randint(
        0, SCREEN_WIDTH), y=random.randint(0, SCREEN_HEIGHT))
    foods.append(chip)
# bug = Sprite(uglyBug, batch=bugsBatch, x=500, y=375)


def headingBetween(pointA, pointB):
    return -np.degrees(atan2(pointB[1] - pointA[1], pointB[0] - pointA[0]))


def distanceBetween(pointA, pointB):
    return sqrt(pow(pointA[0] - pointB[0], 2) + pow(pointA[1] - pointB[1], 2))


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
    # TEST_BUG.move()

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
        bugInfoLabel.text = "Generation {} - {} seconds - {} bugs alive - SPEED {}x".format(genNum, int((time() - genStart) * int(speedModifier)), bugsAlive, int(speedModifier))
        with generationLock:
            bugsStillAlive = False
            for i in range(int(speedModifier)):
                for bug in bugSprites:
                    if bug.visible:
                        bugsStillAlive = True
                        bug.useBrain(foods)

            if not bugsStillAlive:
                bugsAlive = 0


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
            bug.position = (random.randint(BUG_BUFFER, SCREEN_WIDTH -
                                           BUG_BUFFER), random.randint(0, SCREEN_HEIGHT - BUG_BUFFER))
            direction = random.randint(0, 360)
            bug.setSpeedAndDirection(0.00001, direction)
            bug.rotation = direction
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
