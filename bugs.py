import random
import pyglet
from math import atan2, cos, pi, sin, sqrt
import numpy as np


def headingBetween(pointA, pointB):
    return -np.degrees(atan2(pointB[1] - pointA[1], pointB[0] - pointA[0]))


def distanceBetween(pointA, pointB):
    return sqrt(pow(pointA[0] - pointB[0], 2) + pow(pointA[1] - pointB[1], 2))


class Bug(pyglet.sprite.Sprite):
    # The vison arc that the bug can see food particles in
    visionRange = (-60, 60)

    # the width and height of the world that the bugs live in
    worldWidth = 100
    worldHeight = 100

    # The maximum distance between the bug and the food before the bug is considered to be collided with the food
    radius = 16

    maxSpeed = 16
    turnRate = 4

    massPerFood = 0.001
    mass = 0.01
    velocityScaling = 0.1
    baseStarvation = 0.01
    startingHunger = 3

    def __init__(self, img, x=0, y=0, blend_src=770, blend_dest=771, batch=None, group=None, usage='dynamic', subpixel=False):
        super(Bug, self).__init__(img, x=x, y=y, blend_src=blend_src, blend_dest=blend_dest,
                                  batch=batch, group=group, usage=usage, subpixel=subpixel)
        self.hunger = Bug.startingHunger
        self.fitness = 0
        self.brain = None
        self.genome = None
        self.genomeID = None

    def useBrain(self, foodSprites):
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

            if chipDirection >= Bug.visionRange[0] and chipDirection <= Bug.visionRange[1] and chipDistance < minChipDistance:
                minChipDistance = chipDistance
                minChipDirection = chipDirection

            if chipDistance < 16:
                self.fitness += 1
                self.hunger += 1
                # print("\tBug now has {} food in its belly".format(bugHungers[i]))
                chip.position = (random.randint(
                    0, Bug.worldWidth), random.randint(0, Bug.worldHeight))

        # print("{}: {} {} {}".format(i, chipDirection, leftEyeChipDistances, rightEyeChipDistances))

        # TODO Change any of this stuff to your hearts content! Make the bugs smart
        adjustedDirection = minChipDirection / (Bug.visionRange[1] - Bug.visionRange[0])
        adjustedDistance = minChipDistance
        hungerLevel = 1 / self.hunger if self.hunger != 0 else 100000000

        inputs = (adjustedDirection, adjustedDistance, hungerLevel, 1.0)

        output = self.brain.activate(inputs) if self.brain is not None else (0, 0, 0, 0)

        self.rotation += (output[0] - output[1]) * Bug.turnRate
        speed = abs(output[2] - output[3]) * Bug.maxSpeed
        self.position = (self.position[0] + speed * cos(pi * self.rotation / 180), self.position[1] - speed * sin(pi * self.rotation / 180))

        self.position = (max(min(self.position[0], Bug.worldWidth), 0), max(min(self.position[1], Bug.worldHeight), 0))

        self.hunger -= Bug.baseStarvation + 0.5 * (Bug.mass + self.hunger * Bug.massPerFood) * pow(speed * Bug.velocityScaling, 2)

        if self.hunger < 0:
            # print("!!!!! Bug {} starved to death :( !!!!!".format(i))
            # print("\tIt had {} food in its belly".format(bugHungers[i]))
            self.visible = False

class HeadlessBug():
    # The vison arc that the bug can see food particles in
    visionRange = (-60, 60)

    # the width and height of the world that the bugs live in
    worldWidth = 0
    worldHeight = 0

    # The maximum distance between the bug and the food before the bug is considered to be collided with the food
    radius = 16 # TODO NOT BEING USED

    maxSpeed = 16
    turnRate = 4

    massPerFood = 0.001
    mass = 0.01
    velocityScaling = 0.1
    baseStarvation = 0.01
    startingHunger = 3

    def __init__(self):
        self.hunger = Bug.startingHunger
        self.fitness = 0
        self.brain = None
        self.genome = None
        self.genomeID = None
        self.isAlive = False
        self.position = (0, 0)
        self.rotation = 0

    def useBrain(self, foods):
        leftEyeChipDistances = [0, 0, 0]
        rightEyeChipDistances = [0, 0, 0]

        minChipDistance = 10000000
        minChipDirection = 0

        for i in range(len(foods)):
            chip = foods[i]
            chipDirection = headingBetween(
                self.position, chip) - self.rotation
            chipDirection %= 360
            chipDirection + 360
            chipDirection %= 360

            if chipDirection > 180:
                chipDirection -= 360
            elif chipDirection < -180:
                chipDirection += 360

            chipDistance = distanceBetween(
                self.position, chip)

            if chipDirection >= HeadlessBug.visionRange[0] and chipDirection <= HeadlessBug.visionRange[1] and chipDistance < minChipDistance:
                minChipDistance = chipDistance
                minChipDirection = chipDirection

            if chipDistance < 16:
                self.fitness += 1
                self.hunger += 1
                # print("\tBug now has {} food in its belly".format(bugHungers[i]))
                foods[i] = (random.randint(0, HeadlessBug.worldWidth), random.randint(0, HeadlessBug.worldHeight))

        # TODO Change any of this stuff to your hearts content! Make the bugs smart
        adjustedDirection = minChipDirection / (HeadlessBug.visionRange[1] - HeadlessBug.visionRange[0])
        adjustedDistance = minChipDistance
        hungerLevel = 1 / self.hunger if self.hunger != 0 else 100000000

        inputs = (adjustedDirection, adjustedDistance, hungerLevel, 1.0)

        output = self.brain.activate(inputs) if self.brain is not None else (0, 0, 0, 0)

        self.rotation += (output[0] - output[1]) * HeadlessBug.turnRate
        speed = abs(output[2] - output[3]) * HeadlessBug.maxSpeed
        self.position = (self.position[0] + speed * cos(pi * self.rotation / 180), self.position[1] - speed * sin(pi * self.rotation / 180))

        self.position = (max(min(self.position[0], HeadlessBug.worldWidth), 0), max(min(self.position[1], HeadlessBug.worldHeight), 0))

        self.hunger -= HeadlessBug.baseStarvation + 0.5 * (HeadlessBug.mass + self.hunger * HeadlessBug.massPerFood) * pow(speed * HeadlessBug.velocityScaling, 2)

        #print(self.hunger)
        if self.hunger < 0:
            # print("!!!!! Bug {} starved to death :( !!!!!".format(i))
            # print("\tIt had {} food in its belly".format(bugHungers[i]))
            self.isAlive = False
