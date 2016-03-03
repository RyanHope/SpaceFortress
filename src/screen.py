class Screen(object):
    def __init__(self, screen_name):
        # super(self.__class__, self).__init__()
        self.screen_name = screen_name

    def exit_prematurely(self):
        pass

    def debug_keys_acceptable(self):
        return True

    def debug_set_sounds(self, val):
        pass
