# this one *must* be first
import random

import etgg2801

import pysdl2.sdl2 as sdl2
import pysdl2.sdl2.keycode as keycode
from gl import *
from glconstants import *
import time
from Globals import GlobalVars
import ctypes
import BufferManager
import math
from Program import Program
from Sampler import MipSampler, NearestSampler, ClampSampler
from ImageTexture2DArray import ImageTexture2DArray
from math2801 import *
from Camera import Camera
from FullScreenQuad import FullScreenQuad
from GLTFMesh import GLTFMesh
import Text
import Lights
from Framebuffer import Framebuffer
from Blurrer import Blurrer
from ImageTextureCube import ImageTextureCube
from BillboardManager import *
from ParticleSystem import ParticleSystem


def main():
    win = etgg2801.createWindow(width=512, height=512)
    print(glGetString(GL_RENDERER), glGetString(GL_VENDOR), glGetString(GL_VERSION),
          glGetString(GL_SHADING_LANGUAGE_VERSION))
    globs = GlobalVars()
    setup(globs)
    last = time.time_ns() / 1000000000
    DESIRED_FRAMES_PER_SEC = 60
    DESIRED_SEC_PER_FRAME = 1 / DESIRED_FRAMES_PER_SEC
    QUANTUM = 0.005
    accumulated = 0
    while True:
        now = time.time_ns() / 1000000000
        elapsed = now - last
        last = now
        accumulated += elapsed
        while accumulated >= QUANTUM:
            update(QUANTUM, globs)
            accumulated -= QUANTUM
        draw(globs)
        sdl2.SDL_GL_SwapWindow(win)
        end = time.time_ns() / 1000000000
        frameTime = end - now
        leftover = DESIRED_SEC_PER_FRAME - frameTime
        if leftover > 0:
            time.sleep(leftover)


def setup(globs):
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_STENCIL_TEST)
    glDepthFunc(GL_LEQUAL)

    globs.focalRange = 2.0

    globs.keys = set()
    globs.mouseLook = True
    sdl2.SDL_SetRelativeMouseMode(1)

    globs.prog = Program(vs="vs.txt",
                         fs="fs.txt")

    globs.camera = Camera(vec3(0, 1, 2), vec3(0, 1, 0), vec3(0, 1, 0))
    # globs.fbosharp = Framebuffer(512, 512, GL_RGBA8)
    # globs.fboblurry = Framebuffer(512, 512, GL_RGBA8)

    globs.fbo1 = Framebuffer(512, 512, GL_RGBA8, withStencilBuffer=True)
    globs.fbo2 = Framebuffer(512, 512, GL_RGBA8)
    globs.fsq = FullScreenQuad()
    globs.fboprog = Program(vs="fbovs.txt", fs="fbofs.txt")
    # globs.blurrer = Blurrer(globs.fboblurry, 12)
    globs.blurrer_senciel = Blurrer(globs.fbo2, 8)
    globs.skyboxprog = Program(vs="skyboxvs.txt", fs="skyboxfs.txt")

    globs.particle = ParticleSystem(512, vec3(-8.95, 0.2, -1.45), ImageTexture2DArray("smoke.png"))

    # bumpSamlper =
    clampSampler = ClampSampler()
    clampSampler.bind(14)
    mipSampler = MipSampler()
    mipSampler.bind(0)  # color texture
    mipSampler.bind(1)  # emission texture
    mipSampler.bind(2)
    mipSampler.bind(3)  # metallicity/roughness

    nearestSampler = NearestSampler()
    nearestSampler.bind(15)

    globs.skyboxTexture = ImageTextureCube("right.png", "left.png",
                                           "top.png", "bottom.png",
                                           "front.png", "back.png")

    globs.indoormap = ImageTextureCube("px.jpg", "nx.jpg", "py.jpg",
                                       "ny.jpg", "pz.jpg", "nz.jpg")

    glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)
    mipSampler.bind(7)

    globs.meshes = []

    fname = os.path.join(
        os.path.dirname(__file__),
        "bigassets",
        "kitchen.gltf")

    globs.meshes.append(GLTFMesh(fname))
    globs.cubeMesh = GLTFMesh("assets/cube.gltf")

    globs.nontranslucentitems = globs.meshes[0].getItemsNotMatchingName("bookshelfglass")
    globs.translucentitems = globs.meshes[0].getItemsMatchingName("bookshelfglass")

    lightdata = Lights.parseLights(fname)

    lightPositionsAndDirectionalFlag = [None] * len(lightdata)
    spotDirectionsAndCosineSpotEdgeStarts = [None] * len(lightdata)
    lightColorsAndCosineSpotAngleCutoffs = [None] * len(lightdata)

    for i in range(len(lightdata)):
        lightPositionsAndDirectionalFlag[i] = vec4(lightdata[i].position, 1.0)
        spotDirectionsAndCosineSpotEdgeStarts[i] = vec4(0, -1, 0, math.cos(math.radians(lightdata[i].spotCutoffStart)))
        lightColorsAndCosineSpotAngleCutoffs[i] = vec4(lightdata[i].energy * vec3(*lightdata[i].color),
                                                       math.cos(math.radians(lightdata[i].spotCutoffEnd)))

    Program.setUniform("lightPositionsAndDirectionalFlag[0]", lightPositionsAndDirectionalFlag)
    Program.setUniform("spotDirectionsAndCosineSpotEdgeStarts[0]", spotDirectionsAndCosineSpotEdgeStarts)
    Program.setUniform("lightColorsAndCosineSpotAngleCutoffs[0]", lightColorsAndCosineSpotAngleCutoffs)
    Program.setUniform("attenuation", vec3(450, 0, 3.5))

    # for text

    glClearColor(0, 0, 0, 1)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    Text.initialize()
    updateText(globs)
    BufferManager.pushToGPU()


def updateText(globs):
    if globs.mouseLook:
        state = "off"
    else:
        state = "on "

    Text.print(0, f"Tab=Mouselook {state}")
    Text.print(1, "WASD=walk/strafe  QE=turn RF=up/down")


def update(elapsed, globs):
    pumpEvents(globs)

    if keycode.SDLK_w in globs.keys:
        globs.camera.strafeNoUpOrDown(0, 0, 2.0 * elapsed)
    if keycode.SDLK_s in globs.keys:
        globs.camera.strafeNoUpOrDown(0, 0, -2.0 * elapsed)
    if keycode.SDLK_a in globs.keys:
        globs.camera.strafeNoUpOrDown(-2.0 * elapsed, 0, 0)
    if keycode.SDLK_d in globs.keys:
        globs.camera.strafeNoUpOrDown(2.0 * elapsed, 0, 0)
    if keycode.SDLK_q in globs.keys:
        globs.camera.turn(elapsed)
    if keycode.SDLK_e in globs.keys:
        globs.camera.turn(-elapsed)
    if keycode.SDLK_r in globs.keys:
        globs.camera.strafeXYZ(0, elapsed, 0)
    if keycode.SDLK_f in globs.keys:
        globs.camera.strafeXYZ(0, -elapsed, 0)

    globs.particle.update(elapsed)


def pumpEvents(globs):
    ev = sdl2.SDL_Event()
    while True:
        eventOccurred = sdl2.SDL_PollEvent(ctypes.byref(ev))
        if not eventOccurred:
            return
        if ev.type == sdl2.SDL_QUIT:
            sdl2.SDL_Quit()
            sys.exit(0)
        if ev.type == sdl2.SDL_KEYDOWN:
            if ev.key.keysym.sym == keycode.SDLK_F1:
                etgg2801.screenshot("screenshot.png")
                print("Wrote screenshot.png")
            elif ev.key.keysym.sym == keycode.SDLK_TAB:
                globs.mouseLook = not globs.mouseLook
                if globs.mouseLook:
                    sdl2.SDL_SetRelativeMouseMode(1)
                else:
                    sdl2.SDL_SetRelativeMouseMode(0)
                updateText(globs)
            elif ev.key.keysym.sym == keycode.SDLK_ESCAPE:
                sdl2.SDL_Quit()
                sys.exit(0)
            elif ev.key.keysym.sym == keycode.SDLK_1:
                globs.focalRange += 0.2
            elif ev.key.keysym.sym == keycode.SDLK_2:
                globs.focalRange -= 0.2
            globs.keys.add(ev.key.keysym.sym)
        if ev.type == sdl2.SDL_KEYUP:
            globs.keys.discard(ev.key.keysym.sym)
        if ev.type == sdl2.SDL_MOUSEMOTION:
            if globs.mouseLook:
                globs.camera.turnAroundAxis(vec3(0, 1, 0), -0.005 * ev.motion.xrel, )
                globs.camera.pitch(-0.005 * ev.motion.yrel)


def draw(globs):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
    glStencilFunc(GL_ALWAYS, 1, ~0)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
    # globs.fbosharp.setAsRenderTarget(True)
    BufferManager.bind()
    globs.prog.use()
    globs.camera.setUniforms()
    Program.setUniform("forceColorFlag", 0.0)
    Program.setUniform("forceColor", vec4(0.0, 0.0, 0.0, 0.0))
    Program.setUniform("alphaFactor", 1.0)
    Program.setUniform("animationFrame", 1.0)
    Program.setUniform("worldMatrix", mat4.identity())
    Program.setUniform("focalrange", globs.focalRange)
    Program.setUniform("testDepth", 0.0)
    Program.setUniform("elapsed", 0.0)
    globs.indoormap.bind(7)

    glStencilFunc(GL_ALWAYS, 0, 0xff)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

    globs.fbo1.setAsRenderTarget(True)
    globs.meshes[0].draw(toDraw=globs.translucentitems)
    globs.fbo1.unsetAsRenderTarget()

    globs.fbo2.setAsRenderTarget(True)
    glColorMask(0, 0, 0, 0)
    glDepthMask(0)
    glStencilFunc(GL_ALWAYS, 1, 0xff)
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    globs.meshes[0].draw(toDraw=globs.translucentitems)

    glColorMask(1, 1, 1, 1)
    glDepthMask(1)

    glStencilFunc(GL_EQUAL, 1, 0xff)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

    globs.fbo1.depthtexture.bind(15)
    Program.setUniform("testDepth", 1.0)
    globs.meshes[0].draw(toDraw=globs.nontranslucentitems)
    Program.setUniform("testDepth", 0.0)
    # globs.fbo1.depthtexture.unbind(15)

    globs.fbo2.unsetAsRenderTarget()

    # globs.fbo2.dump("test")

    glStencilFunc(GL_ALWAYS, 0, 0xff)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
    # globs.blurrer.blur(0)
    globs.blurrer_senciel.blur(0)

    glStencilFunc(GL_ALWAYS, 1, 0xff)
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    glColorMask(0, 0, 0, 0)
    globs.meshes[0].draw(toDraw=globs.translucentitems)
    glColorMask(1, 1, 1, 1)

    glStencilFunc(GL_ALWAYS, 0, 0xff)
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    globs.meshes[0].draw(toDraw=globs.nontranslucentitems)

    glStencilFunc(GL_EQUAL, 1, 0xff)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
    glDisable(GL_DEPTH_TEST)
    globs.fboprog.use()
    globs.fbo2.texture.bind(0)
    globs.fsq.draw()

    glEnable(GL_DEPTH_TEST)
    globs.prog.use()
    globs.meshes[0].draw(toDraw=globs.translucentitems)

    glStencilFunc(GL_ALWAYS, 0, 0xff)

    globs.particle.draw()

    globs.skyboxprog.use()
    globs.skyboxTexture.bind(7)
    globs.cubeMesh.draw()

    # globs.fbosharp.unsetAsRenderTarget()
    # globs.fboblurry.setAsRenderTarget(False)
    # glBindFramebuffer(GL_READ_FRAMEBUFFER, globs.fbosharp.fbo)
    # glBlitFramebuffer(0, 0, globs.fbosharp.w, globs.fbosharp.h,
    #                   0, 0, globs.fboblurry.w, globs.fboblurry.h,
    #                   GL_COLOR_BUFFER_BIT,
    #                   GL_NEAREST)
    # globs.fboblurry.unsetAsRenderTarget()

    # globs.fboprog.use()
    # globs.fbosharp.texture.bind(0)
    # globs.fboblurry.texture.bind(1)
    # globs.fbosharp.depthtexture.bind(15)
    # globs.fsq.draw()
    # Text.draw()
    # glStencilFunc(GL_ALWAYS, 1, ~0)
    # glStencilOp(GL_KEEP, GL_KEEP, GL_INCR)


main()
