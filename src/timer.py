class Timer(object):
    """basic game timer"""
    def __init__(self, val=0):
        self.time = val

    def elapsed(self):
        """time elapsed since timer created"""
        return self.time

    def reset(self, val=0):
        """resets timer to current time"""
	self.time = val

    def tick(self,ms):
	self.time += ms

    def check(self):
        pass
