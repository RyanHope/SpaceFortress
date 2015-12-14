class Timer(object):
    """basic game timer"""
    def __init__(self):
        self.time = 0

    def elapsed(self):
        """time elapsed since timer created"""
        return self.time

    def reset(self):
        """resets timer to current time"""
	self.time = 0
    def tick(self,ms):
	self.time += ms

    def check(self):
        pass
