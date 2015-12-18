class Press(object):
    def __init__(self, id):
        self.id = id

class Release(object):
    def __init__(self, id):
        self.id = id

class KeyState(object):
    def __init__(self):
        self.keys = {'left': False,
                     'right': False,
                     'thrust': False,
                     'fire': False,
                     'iff': False,
                     'shots': False,
                     'pnts': False}
        self.events = []

    def reset_tick(self):
        self.events = []
