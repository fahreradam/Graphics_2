import BufferManager
from gl import *
from glconstants import *
from Program import Program
from BufferTexture import BufferTexture

class BillboardManager:
    prog = None
    CHUNK_SIZE = 128

    # centers = list of vec3
    def __init__(self, centers, texture):
        assert len(centers) % BillboardManager.CHUNK_SIZE == 0
        self.numInstances = len(centers) // BillboardManager.CHUNK_SIZE

        if BillboardManager.prog == None:
            BillboardManager.prog = Program(vs="billboardvs.txt", fs="billboardfs.txt")
        self.tex = texture
        tmp = []
        for p in centers:
            tmp.append(p.x)
            tmp.append(p.y)
            tmp.append(p.z)
            tmp.append(1)  # padding

        self.bufftex = BufferTexture(
            array.array("f", tmp),
            GL_RGBA32F)

        self.numBillboards = len(centers)
        sizex = 1
        sizey = 1
        positiondata = []
        texturedata = []
        normaldata = []
        indexdata = []
        tangentdata = []
        for j in range(BillboardManager.CHUNK_SIZE):
            positiondata += [j, 0, 0] * 4
            texturedata += [0, 0, 0, 1, 1, 1, 1, 0]
            normaldata += [sizex, sizey, 0] * 4
            i = j * 4
            indexdata += [i, i + 1, i + 2, i, i + 2, i + 3]
            tangentdata += [0, 0, 0, 0] * 4
        tmp = BufferManager.addIndexedData(
            positiondata=positiondata,
            basetexturedata=texturedata,
            bumptexturedata=texturedata,
            normaldata=normaldata,
            indexdata=indexdata,
            tangentdata=tangentdata
        )
        self.vertexOffset, self.indexStart = tmp

    def draw(self):
        glDepthMask(0)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        oldprog = Program.current
        BillboardManager.prog.use()
        self.tex.bind(0)
        self.bufftex.bindTexture(8)
        glDrawElementsInstancedBaseVertex(
            GL_TRIANGLES, BillboardManager.CHUNK_SIZE*6,
            GL_UNSIGNED_INT, self.indexStart,
            self.numInstances, self.vertexOffset )
        if oldprog:
            oldprog.use()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(1)