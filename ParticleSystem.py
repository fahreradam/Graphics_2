from BillboardManager import BillboardManager
from math2801 import *
from glconstants import *
from gl import *
from BufferTexture import BufferTexture
import random
from Program import Program

class ParticleSystem:
    updateprog = None

    def __init__(self, numP, initialPosition, texture):
        if ParticleSystem.updateprog == None:
            ParticleSystem.updateprog = Program(cs="pscs.txt")

        self.numParticles = numP
        self.initialPosition = initialPosition

        tmp = [vec3(0, 0, 0)] * numP
        self.bbmanager = BillboardManager(tmp, texture)
        self.velData = BufferTexture(
            array.array("f", [0, 0, 0, 0] * numP),
            GL_RGBA32F)
        self.reset()

    def reset(self):
        tmp = array.array("f",
                          [self.initialPosition.x,
                           self.initialPosition.y,
                           self.initialPosition.z,
                           1
                           ] * self.numParticles
                          )
        for i in range(3, len(tmp), 4):
            tmp[i] = random.uniform(1.5, 5)

            self.bbmanager.bufftex.bindBuffer(GL_ARRAY_BUFFER)
            glBufferSubData(GL_ARRAY_BUFFER,
            0, self.numParticles * 16,
            array.array("f", tmp))


            self.bbmanager.bufftex.bindBuffer(GL_ARRAY_BUFFER)

        glBufferSubData(GL_ARRAY_BUFFER,
                        0,  # starting offset
                        self.numParticles * 16,  # size in bytes
                        tmp
                        )
        tmp = array.array("f", [])
        for i in range(self.numParticles):
            v = vec3(random.uniform(-0.5, 0.5),
                     random.uniform(0, 1),
                     random.uniform(-0.5, 0.5))
            # optional: Normalize v
            tmp.append(v.x)
            tmp.append(v.y)
            tmp.append(v.z)
            tmp.append(0)

        self.velData.bindBuffer(GL_ARRAY_BUFFER)
        glBufferSubData(GL_ARRAY_BUFFER,
                        0,
                        self.numParticles * 16,
                        tmp)

    def update(self, elapsed):
        oldprog = Program.current
        ParticleSystem.updateprog.use()
        self.bbmanager.bufftex.bindImage(0)  # position data
        self.velData.bindImage(1)  # velocity data
        Program.setUniform("elapsed", elapsed)
        ParticleSystem.updateprog.dispatch(
            self.numParticles // 64, 1, 1)
        glMemoryBarrier(GL_ALL_BARRIER_BITS)
        sync = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0)
        glClientWaitSync(sync, GL_SYNC_FLUSH_COMMANDS_BIT, -1)
        glDeleteSync(sync)
        if oldprog:
            oldprog.use()

    def draw(self):
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        self.bbmanager.draw()
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

