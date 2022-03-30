import enum
import pysdl2.sdl2.keycode as keycode


class BulletState(enum.Enum):
    IDLE = 1
    CHARGING = 2
    FIRING = 3
    FLASHING = 4


class BulletStateMachine:
    def __init__(self):
        self.currentState = BulletState.IDLE
        self.chargeAmount = 0
        self.fire = False

    def update(self, keysbefore, keysnow, elapsed):
        if self.currentState == BulletState.IDLE:
            if keycode.SDLK_SPACE in keysnow and keycode.SDLK_SPACE not in keysbefore:
                self.currentState = BulletState.CHARGING
        if self.currentState == BulletState.CHARGING:
            if not keycode.SDLK_SPACE in keysnow:
                self.currentState = BulletState.FIRING
                self.fire = True
        if self.currentState == BulletState.CHARGING:
            if self.chargeAmount < 1:
                self.chargeAmount = self.chargeAmount + (0.1 * elapsed)

        if self.currentState == BulletState.FIRING:
            if self.chargeAmount == 0:
                self.currentState = BulletState.IDLE
