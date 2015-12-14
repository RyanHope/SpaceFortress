import pygame
import socket
import drawing
import lisp
import sys

class Model(object):
    def __init__(self, port, display_level, line_endings):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('',port))
        self.commands = []
        self.objects = None
        self.display_level = display_level
        self.line_endings = '\r\n' if line_endings == 'crlf' else '\n'
        self.events = []

    def update_display_level(self, app, level):
        if level > 0:
            # create the screen if necessary
            if pygame.display.get_surface() == None:
                pygame.display.set_mode((1024, 768))
            if self.display_level == 0:
                app.load_display_assets()
                app.score.load_display_assets()
        self.display_level = level

    def send_objects(self, mode, delay_duration=None):
        if self.objects:
            self.objects['mode'] = mode
            if delay_duration:
                self.objects['delay_duration'] = delay_duration
            self.channel.send((lisp.lispify(self.objects) + self.line_endings).encode('utf-8'))
            self.objects = None

    def wait_for_connection(self):
        if self.display_level > 0:
            font = pygame.font.Font("fonts/freesansbold.ttf", 20)
            drawing.fullscreen_message(pygame.display.get_surface(),
                                       [drawing.text("Waiting for model...", font, color=(255,255,0))],
                                       drawing.text("",font))
            pygame.display.flip()
        self.socket.listen(1)
        self.channel, details = self.socket.accept()
        self.channel.setblocking(1)

    def parse_event(self, args):
        if (args[0] == 'quit'):
            event = pygame.event.Event(pygame.QUIT)
        elif (args[0] == 'keydown'):
            event = pygame.event.Event(pygame.KEYDOWN, key=int(args[1]), mod=int(args[2]))
        elif (args[0] == 'keyup'):
            event = pygame.event.Event(pygame.KEYUP, key=int(args[1]), mod=int(args[2]))
        else:
            raise Exception("Not a valid event ID: %s"%args[0])
        return event

    def clear_events(self):
        self.events = []

    def read_command(self):
        if len(self.commands) == 0:
            buf = self.channel.recv(4096)
            if not buf:
                print "Model disconnected."
                sys.exit()
            self.commands = buf.lower().splitlines()
        return self.commands.pop(0).split(' ')

    def get_event(self, app):
        self.send_objects('events')
        while True:
            args = self.read_command()
            if args[0] in ['quit','keydown','keyup']:
                self.events.append(self.parse_event(args))
            elif args[0] == 'continue':
                break
            elif args[0] == 'drawing':
                self.update_display_level(app, int(args[1]))
            # else:
            #     self.channel.send('error unknown command: %s\n'%args[0])
        events = self.events
        self.events = []
        return events

    def delay(self, app, ms):
        self.send_objects('delay', ms)
        while True:
            args = self.read_command()
            if args[0] in ['quit','keydown','keyup']:
                self.events.append(self.parse_event(args))
            elif args[0] == 'continue':
                break
            elif args[0] == 'drawing':
                self.update_display_level(app, int(args[1]))
            # else:
            #     self.channel.send('error unknown command: %s\n'%args[0])
