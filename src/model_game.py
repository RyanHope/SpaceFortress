import copy
import lisp
import model_socket
import game

class ModelGame(game.Game):
    def __init__(self, conf, game_name, game_number, channel):
        super(self.__class__, self).__init__(conf, game_name, game_number)
        self.channel = channel
        self.commands = []
        self.quit = False
        self.objects = None
        self.line_endings = '\r\n' if self.config['model_line_endings'] == 'crlf' else '\n'
        # Hardcoded key bindings for backwards compatibility. The
        # model also accepts the action name.
        self.key_bindings = {'119': 'thrust',
                              '97': 'left',
                             '100': 'right',
                              '32': 'fire',
                             '106': 'iff',
                             '107': 'shots',
                             '108': 'pnts'}

    def open_logs(self):
        self.log.open_gamelogs(self.config)

    def delay(self, ms):
        self.set_objects(self.get_world_state_for_model('game'))
        self.send_objects('delay', ms)
        while True:
            args = self.channel.read_command()
            if args[0] == 'quit':
                self.quit = True
            elif args[0] == 'continue':
                break
        self.gameTimer.tick(ms)

    def now(self):
        return 0

    def draw_world(self):
        pass

    def play_sound(self, sound_id):
        pass

    def set_objects(self, objects):
        self.objects = copy.copy(objects)

    def send_objects(self, mode, delay_duration=None):
        if self.objects:
            self.objects['mode'] = mode
            if delay_duration:
                self.objects['delay_duration'] = delay_duration
            self.channel.send(self.objects)
            self.objects = None

    def decode_keycode (self, code):
        if code in ['thrust', 'left', 'right', 'fire', 'iff', 'shots', 'pnts']:
            return code
        elif code in self.key_bindings:
            return self.key_bindings[code]
        else:
            return None

    def reset_event_queue(self):
        # self.commands = ['continue']
        pass

    def encode_keycode(self, code):
        if code in ['thrust', 'left', 'right', 'fire', 'iff', 'shots', 'pnts']:
            for k,v in self.key_bindings.iteritems():
                if code == v:
                    return int(k)
        elif code in self.key_bindings:
            return int(code)
        else:
            return None

    def process_input_events(self):
        self.key_state.reset_tick()
        self.send_objects('events')
        keys = []
        while True:
            try:
                args = self.channel.read_command()
            except model_socket.disconnected:
                self.quit = True
                break
            if (args[0] == 'quit'):
                self.quit = True
            elif (args[0] == 'keydown'):
                k = self.decode_keycode(args[1])
                if k != None:
                    self.press_key(k)
                    keys.append([2,self.encode_keycode(k),0])
            elif (args[0] == 'keyup'):
                k = self.decode_keycode(args[1])
                if k != None:
                    self.release_key(k)
                    keys.append([3,self.encode_keycode(k),0])
            elif args[0] == 'continue':
                break
        b = [self.tinc]
        b.append(keys)
        self.log.write_keys(b)

    def run(self):
        self.start()
        while not self.quit:
            self.gameTimer.tick(33)
            self.step_one_tick()
            if self.cur_time >= int(self.config["game_time"]):
                break
        if self.quit:
            self.log.log_premature_exit()
            self.log.close_gamelogs()
        else:
            self.finish()
        return self.quit
