#FullScreenQuad.py

import BufferManager
from gl import *
from glconstants import *

class FullScreenQuad:
    def __init__(self):
        self.delta, self.indexStart = BufferManager.addIndexedData(
            positiondata =  [-1,-1,0,   1,-1,0,   1,1,0,   -1,1,0   ],
            basetexturedata=    [ 0,0,      1,0,      1,1,     0,1      ],
            normaldata=     [ 0,0,1,    0,0,1,    0,0,1,   0,0,1    ],
            indexdata = [0,1,2,    0,2,3],
            bumptexturedata= [  0,0,      1,0,      1,1,     0,1    ],
            tangentdata=[-1,-1,0,0 ,  1,-1,0,0,   1,1,0,0  , -1,1,0,0   ],

        )

    def draw(self):
        glDrawElementsBaseVertex( GL_TRIANGLES,
            6, GL_UNSIGNED_INT, self.indexStart, self.delta )
