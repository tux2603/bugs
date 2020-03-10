import pyglet
import numpy as np
from math import sin, cos, atan, atan2, sqrt


class Sprite(pyglet.sprite.Sprite):
    # TODO drawBoundingRectangle
    # TODO isClicked
    # TODO getBoundingRectangle
    # TODO reflect
    # TODO isCollided

    # The maximum speed at which the sprite can travel, used for acceleration methods
    maxSpeed = 10

    # The distance that the sprite travles per clock tick
    _velocity = (0, 0)

    # Number of game ticks that the sprite has to remain alive
    ttl = -1

    # A two dimensional array of which pixels in the sprite are opaque/transparent
    pixelMap = None

    def __init__(self, img, x=0, y=0, blend_src=770, blend_dest=771, batch=None, group=None, usage='dynamic', subpixel=False):
        super(Sprite, self).__init__(img, x=x, y=y, blend_src=blend_src, blend_dest=blend_dest,
                                     batch=batch, group=group, usage=usage, subpixel=subpixel)
        self.setImage(img)

    # Sets the image of the sprite and updates the pixel map data used for collison detection
    def setImage(self, img):
        # Set the image
        self.image = img

        # Get raw pixel data out of the image
        rawData = img.get_image_data()
        colorFormat = 'RGBA'
        pitch = rawData.width * len(colorFormat)
        pixelData = rawData.get_data(colorFormat, pitch)

        self.pixelMap = np.zeros((rawData.width, rawData.height), np.int8)

        # load the transparency values from the raw data string into the array
        for x in range(rawData.width):
            for y in range(rawData.height):
                self.pixelMap[x][y] = pixelData[(
                    x + y * rawData.width) * len(colorFormat) + 3]

    # Gets a transformation matrix for the sprite
    def getTransformMatrix(self):
        return Matrix.createTranslation((-self.image.anchor_x / self.scale_x, -self.image.anchor_y / self.scale_y)) * \
            Matrix.createRotation(np.radians(self.rotation)) * Matrix.createScale((self.scale_x, self.scale_y)) * \
            Matrix.createTranslation(
                (self.position[0] + self.image.anchor_x, self.position[1] + self.image.anchor_y))

    def getWidth(self):
        return self.image.width * self.scale_x

    def getHeight(self):
        return self.image.height * self.scale_y

    def getCenter(self):
        return (self.getWidth() / 2, self.getHeight() / 2)

    def getSpeed(self):
        return sqrt(self._velocity[0] * self._velocity[0] + self._velocity[1] * self._velocity[1])

    def setSpeedAndDirection(self, speed, angle):
        rad = -np.radians(angle)

        if speed > self.maxSpeed:
            speed = self.maxSpeed

        self._velocity = (speed * cos(rad), speed * sin(rad))

    def getDirectionAngle(self):
        angle = -np.degrees(atan2(self._velocity[1], self._velocity[0]))
        if angle < 0:
            angle += 360
        return angle

    def setDirectionAngle(self, newAngle):
        speed = self.getSpeed()
        self.setSpeedAndDirection(speed, newAngle)

    def setSpeed(self, newSpeed):
        directionAngle = self.getDirectionAngle()
        self.setSpeedAndDirection(newSpeed, directionAngle)

    def changeDirectionAngle(self, delta):
        delta = -np.radians(delta)
        self._velocity = (self._velocity[0] * cos(delta) + self._velocity[1] * -sin(
            delta), self._velocity[0] * sin(delta) + self._velocity[1] * cos(delta))

    def getDirectionTo(self, other):
        deltaPos = self.position - other.position
        angle = np.degrees(atan2(deltaPos[1], deltaPos[0]))
        if angle < 0:
            angle += 360
        return angle

    def setVelocity(self, newVelocity):
        newSpeed = sqrt(
            newVelocity[0] * newVelocity[0] + newVelocity[1] * newVelocity[1])

        reductionFactor = 1

        if newSpeed > self.maxSpeed:
            reductionFactor = self.maxSpeed / newSpeed

        self._velocity = (
            newVelocity[0] * reductionFactor, newVelocity[1] * reductionFactor)

    def setVelocityX(self, newVelocity):
        self.setVelocity((newVelocity, self._velocity[1]))

    def setVelocityY(self, newVelocity):
        self.setVelocity((self._velocity[0], newVelocity))

    def _checkTTL(self):
        if self.ttl >= 0:
            self.ttl -= 1

        elif self.ttl == 0:
            self.visible = False

        return self.visible

    def move(self):
        if not self._checkTTL():
            return False

        self.position = (
            self.position[0] + self._velocity[0], self.position[1] + self._velocity[1])

        return True

    def accelerate(self, acceleration):
        if isinstance(acceleration, (tuple, list)):
            ax = acceleration[0]
            ay = acceleration[1]
        else:
            ax = acceleration * self._velocity[0] / \
                (self._velocity[0] + self._velocity[1])
            ay = acceleration * self._velocity[1] / \
                (self._velocity[0] + self._velocity[1])

        self._velocity = (self._velocity[0] + ax, self._velocity[1] + ay)

    def getDirectionRangeTo(self, objectLocation, objectRadius):
        dx = object[0] - self.position[0]
        dy = object[1] - self.position[1]

        distance = sqrt(dx*dx + dy*dy)
        direction = atan2(dy, dx)
        directionDelta = atan(objectRadius / distance)
        return (direction + directionDelta, direction - directionDelta)
        


class Ground(Sprite):
    blocksTop = False
    blocksBottom = False
    blocksLeft = False
    blocksRight = False
    buoyancy = 0

    def setAttributes(self, blocksTop=False, blocksBottom=False, blocksLeft=False, blocksRight=False, buoyancy=0):
        self.blocksTop = blocksTop
        self.blocksBottom = blocksBottom
        self.blocksLeft = blocksLeft
        self.blocksRight = blocksRight
        self.buoyancy = buoyancy


class Matrix():
    @staticmethod
    def createTranslation(offset):
        x, y = offset
        return Matrix(((1, 0, x), (0, 1, y), (0, 0, 1)))

    @staticmethod
    def createRotation(theta):
        return Matrix(((cos(theta), -sin(theta), 0), (sin(theta), cos(theta), 0), (0, 0, 1)))

    @staticmethod
    def createScale(svale):
        scaleX, scaleY = scaleX
        return Matrix(((scaleX, 0, 0), (0, scaleY, 0), (0, 0, 1)))

    def __init__(self, matrix=None):
        self._array = np.zeros((3, 3))

        if matrix is None:
            self._array[0][0] = 1
            self._array[1][1] = 1
            self._array[2][2] = 1
        else:
            for x in range(3):
                for y in range(3):
                    self._array[x][y] = matrix[x][y]

    def __mul__(self, other):
        if isinstance(other, Matrix):
            return Matrix(self._array.dot(other._array))
        else:
            return Matrix(self._array.dot(other))

    def invert(self):
        self._array = np.linalg.inv(self._array)
