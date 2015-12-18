import os
import re
import codecs
import game

class SimGame(game.Game):
    def __init__(self,conf, game_name, game_number):
        super(self.__class__, self).__init__(conf, game_name, game_number, None)
        # FIXME: hard code the standard key bindings because we don't
        # want to depend on pygame.
        self.key_bindings = {119: 'thrust',
                              97: 'left',
                             100: 'right',
                              32: 'fire',
                             106: 'iff',
                             107: 'shots',
                             108: 'pnts'}
        self.real_time = 0

    def open_logs(self):
        self.log.open_simulate_logs()
        self.extract_real_times()

    def delay(self, ms):
        self.gameTimer.tick(ms)

    def now(self):
        return self.real_time

    def extract_real_times(self):
        tempname = os.path.join(self.log.datapath,"%s-%s-%d.dat"%(self.log.id, self.log.session, self.log.game))
        self.real_times = []
        self.game_times = []
        if os.path.exists(tempname):
            with codecs.open(tempname,'r','utf-8') as s:
                for l in s:
                    if l[0] == '#':
                        continue
                    else:
                        m = re.match("^(\d+) (\d+\.\d+) (\d+) ", l)
                        if m == None:
                            raise Exception('failed to parse: %s'%l)
                        self.real_times.append(float(m.group(2)))
                        self.game_times.append(int(m.group(3)))

    def simulate_get_keys(self):
        ret = self.log.simulate_next_frame()
        if len(self.real_times) > 0:
            self.real_time = self.real_times.pop(0)
        if len(self.game_times) > 0:
            self.cur_time_override = self.game_times.pop(0)
        self.keys = ret[1]
        # return the time increment
        return ret[0]

    def process_input_events(self):
        self.key_state.reset_tick()
        for key in self.keys:
            t = key[0]
            k = key[1]
            m = key[2]
            if k in self.key_bindings:
                if t == 2:
                    self.press_key(self.key_bindings[k])
                elif t == 3:
                    self.release_key(self.key_bindings[k])
                else:
                    raise Exception('Unknown event type')

    def draw_world(self):
        pass

    def play_sound(self, sound_id):
        pass

    def run(self):
        self.start()
        while True:
            tinc = self.simulate_get_keys()
            self.gameTimer.tick(tinc)
            self.step_one_tick()
            if self.cur_time >= int(self.config["game_time"]):
                break
        self.finish()
