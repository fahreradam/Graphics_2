from gl import *
from glconstants import *
import array


class BufferTexture:
    def __init__(self, initialData, fmt):
        tmp = array.array("I", [0])
        D = initialData.tobytes()
        glGenBuffers(1, tmp)
        self.buff = tmp[0]
        glBindBuffer(GL_TEXTURE_BUFFER, self.buff)
        glBufferData(GL_TEXTURE_BUFFER, len(D), D,
                     GL_STATIC_DRAW)
        glGenTextures(1, tmp)
        self.tex = tmp[0]
        glBindTexture(GL_TEXTURE_BUFFER, self.tex)
        glTexBuffer(GL_TEXTURE_BUFFER, fmt, self.buff)
        self.fmt = fmt

    def bindTexture(self, unit):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_BUFFER, self.tex)

    def bindBuffer(self, target=GL_TEXTURE_BUFFER):
        glBindBuffer(target, self.buff)

    def bindImage(self, idx):
        glBindImageTexture(idx, self.tex,
                           0, 0, 0,  # mipLevel, isLayered, layerNum
                           GL_READ_WRITE,  # permissions
                           self.fmt)

    def dump(self, count):
        tex.bindBuffer()
        tmp = array.array("f", [0] * count * 4)
        # 16=size of vec4, in bytes
        glGetBufferSubData(GL_TEXTURE_BUFFER, 0, count * 16, tmp)
        for i in range(0, len(tmp), 4):
            print("buffer[", i, "]=", tmp[i:i + 4])
