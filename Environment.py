import math
import random
import pysdl2.sdl2 as sdl2
import pysdl2.sdl2.keycode as keycode
from Program import Program
from gl import *
from glconstants import *
import BufferManager
from Mesh import Mesh
from math2801 import *
import copy


class Emitter:
    def __init__(self, amount_num):
        self.bouncers = []
        self.amount = amount_num
        self.run = True
        while self.run:
            self.bouncers.append(Virus())
            if len(self.bouncers) == self.amount:
                self.run = False

    def draw(self):
        for d in self.bouncers:
            d.draw()

    def update(self, elapsed, bullet, scale):
        for u in self.bouncers:
            u.update(elapsed, bullet, scale)


class Player:
    mesh = None

    def __init__(self):
        # if Player.mesh is None:
        #     Player.mesh = Mesh("stickfigure.obj")

        self.direction = []
        self.position = vec3(0, 0, 1)
        self.speed = 0.2
        self.scale = 1
        self.color = vec3(1, 0, 0)
        self.frame = 0.0
        self.alpha = 1

    def update(self, scale):

        if self.position.x <= -scale.x:
            self.position.x = -scale.x
        if self.position.x >= scale.x:
            self.position.x = scale.x
        if self.position.y <= -scale.y:
            self.position.y = -scale.y
        if self.position.y >= scale.y:
            self.position.y = scale.y
        self.frame += 0.05
        if self.frame >= 32:
            self.frame = 0.0

    def draw(self):
        Program.setUniform("alpha", self.alpha)
        Program.setUniform("objcolor", self.color)
        Program.setUniform("worldMatrix", translation(self.position.x, self.position.y, 0))
        Program.setUniform("frame", self.frame)
        Player.mesh.draw()


class Virus:
    mesh = None

    def __init__(self):
        # if Virus.mesh is None:
        #     Virus.mesh = Mesh("virus.obj")
        self.direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self.position = vec2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.speed = 0.01
        self.color = vec3(1, 1, 0)
        self.size = 5
        self.alpha = 1
        self.scale = 0.1
        self.frame = 0.0
        self.dead = False
        self.radius = 0.25
        self.rotate = 0

    def update(self, elapsed, bullet, scale):
        self.rotate += 0.003
        self.radius = self.radius * translation(self.scale, 1, 1)
        self.position[0] += self.speed * self.direction[0]
        self.position[1] += self.speed * self.direction[1]
        if self.position[0] <= -1.01 * scale.x:
            self.direction[0] *= -1
        if self.position[0] >= 1.01 * scale.x:
            self.direction[0] *= -1 * scale.y
        if self.position[1] <= -1.01 * scale.y:
            self.direction[1] *= -1 * scale.y
        if self.position[1] >= 1.01 * scale.y:
            self.direction[1] *= -1 * scale.y
        self.scale += .02 * elapsed
        if self.scale >= 5:
            self.scale = 5
        self.frame += 0.015
        if self.frame >= 15:
            self.frame = 0
        if bullet.displacement.x != 0:
            if ((((bullet.position.x + 0.1 + bullet.displacement.x) - self.position.x) **2) +
                ((bullet.position.y + 0.3 + bullet.displacement.y) - self.position.y) **2)**(1/2) <=(bullet.radius + self.radius[0][0]):
                self.dead = True
        if self.dead:
            self.alpha -= 0.02


    def draw(self):
        # glScissor(self.position[0], self.position[1], self.size, self.size)
        # glClearColor(*self.color)
        # glClear(GL_COLOR_BUFFER_BIT)
        Program.setUniform("alpha", self.alpha)
        Program.setUniform("worldMatrix",
                           (axisRotation(vec3(0,0,1), self.rotate * math.pi) * scaling(self.scale, self.scale, 1) * translation(self.position.x, self.position.y, 0)))
        Program.setUniform("objcolor", self.color)
        Program.setUniform("frame", self.frame)
        Virus.mesh.draw()


class Bullet:
    mesh = None

    def __init__(self, position):
        # if Bullet.mesh is None:
        #     Bullet.mesh = Mesh("bullet.obj")
        self.color = vec3(0, 1, 0)
        self.alpha = 1
        self.position = position
        self.scale = 0.1
        self.displacement = vec2(0, 0)
        self.dead = False
        self.time = 0
        self.rate = 0.003
        self.radius = 0.4 * self.scale

    def update(self, state):
        if state.fire:
            self.displacement.x += (state.chargeAmount * 0.02)
            self.time = self.time + self.rate
            self.alpha = self.alpha - (self.rate*(1/state.chargeAmount))

            if self.time >= state.chargeAmount:
                state.chargeAmount = 0
                self.displacement.x = 0
                self.alpha = 1
                self.time = 0
                state.fire = False
        if self.position.x + self.displacement.x > 1:
            self.dead = True
        if self.position.x + self.displacement.x < -1:
            self.dead = True
        if self.position.y + self.displacement.y > 1:
            self.dead = True
        if self.position.y + self.displacement.y < -1:
            self.dead = True

    def draw(self):
        Program.setUniform("alpha", self.alpha)
        Program.setUniform("worldMatrix", (scaling(self.scale, self.scale, 1) *
                                           translation(self.position.x + 0.1 + self.displacement.x, self.position.y + 0.3 + self.displacement.y, 0)))
        Program.setUniform("objcolor", self.color)
        Bullet.mesh.draw()


class Hexagons:
    def __init__(self):
        self.center_point = [0, 0]
        self.position = [self.center_point[0] - 0.2, self.center_point[1] + 0.35, 0,  # Top
                         self.center_point[0] + 0.2, self.center_point[1] + 0.35, 0,  # Top
                         self.center_point[0], self.center_point[1], 0,  # Top
                         self.center_point[0] + 0.2, self.center_point[1] + 0.35, 0,
                         self.center_point[0] + 0.4, self.center_point[1], 0,
                         self.center_point[0], self.center_point[1], 0,
                         self.center_point[0] + 0.2, self.center_point[1] - 0.35, 0,
                         self.center_point[0] + 0.4, self.center_point[1], 0,
                         self.center_point[0], self.center_point[1], 0,
                         self.center_point[0] - 0.2, self.center_point[1] + 0.35, 0,
                         self.center_point[0] - 0.4, self.center_point[1], 0,
                         self.center_point[0], self.center_point[1], 0,
                         self.center_point[0] - 0.2, self.center_point[1] - 0.35, 0,
                         self.center_point[0] - 0.4, self.center_point[1], 0,
                         self.center_point[0], self.center_point[1], 0,
                         self.center_point[0] - 0.2, self.center_point[1] - 0.35, 0,
                         self.center_point[0] + 0.2, self.center_point[1] - 0.35, 0,
                         self.center_point[0], self.center_point[1], 0]
        self.positiondata = [self.center_point[0], self.center_point[1], 0,
                             self.center_point[0] - 0.2, self.center_point[1] + 0.35, 0,
                             self.center_point[0] + 0.2, self.center_point[1] + 0.35, 0,
                             self.center_point[0] + 0.4, 0, 0,
                             self.center_point[0] + 0.2, self.center_point[1] - 0.35, 0,
                             self.center_point[0] - 0.2, self.center_point[1] - 0.35, 0,
                             self.center_point[0] - 0.4, 0, 0]
        self.index = [1, 0, 2, 2, 0, 3, 3, 0, 4, 4, 0, 5, 5, 0, 6, 6, 0, 1]
        self.startingVertexNumber, self.indexOffset = BufferManager.addIndexedData(positiondata=self.positiondata,
                                                                                   indexdata=self.index)

    def setup(self):
        BufferManager.addData(self.position)
        BufferManager.pushToGPU()

    def draw(self):
        glDrawElementsBaseVertex(GL_TRIANGLES, 18, GL_UNSIGNED_INT, self.indexOffset, self.startingVertexNumber)
