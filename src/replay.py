from __future__ import division
import math
import re
import sys
import argparse
import os
import pygame
# from pygame.locals import *

from object import Object
from Vector2D import Vector2D
import sfdialog

DRAG_START = 1
DRAG_STOP  = 2

class button():
    def __init__(self, text, font, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.surf = font.render(text, 1, (255,255,0))
        self.surf_rect = self.surf.get_rect()
        self.surf_rect.centerx = self.rect.centerx
        self.surf_rect.centery = self.rect.centery

    def draw(self, screen, filled=False):
        pygame.draw.rect(screen, (0,150,0) if filled else (0,255,0), self.rect, 0 if filled else 1)
        screen.blit(self.surf, self.surf_rect)

    def clicked(self, ev):
        return self.rect.collidepoint(ev.pos)

class snapshot():
    def __init__(self, line):
        self.parse_line(line)

    def parse_projectiles(self, triplets):
        ret = []
        if len(triplets) > 0:
            nums = triplets.rstrip(' ').split(' ')
            #print(triplets, nums)
            for i in range(0,len(nums), 3):
                o = Object()
                o.position = Vector2D(float(nums[i]), float(nums[i+1]))
                o.orientation = float(nums[i+2])
                ret.append(o)
        return ret

    def parse_line(self, line):
        m = re.match("(\d+) (\d+\.\d+) (\d+) (y|n) (-|-?\d+\.\d+) (-|-?\d+\.\d+) (-|-?\d+\.\d+) (-|-?\d+\.\d+) (-|\d+\.\d+) (y|n) (\d+\.\d+|-) (\d+\.\d+|-) (y|n) (-|\d+(?:\.\d+)?) \[((?:-?\d+\.\d+ )*)\] \[((?:-?\d+\.\d+ )*)\] (-) (-?\d+) (-?\d+) (-?\d+) (-?\d+) ([A-Z-]) (\d+) (-?\d+) (inf|\d+) (y|n) (y|n) (y|n) (y|n) (y|n) (y|n) (y|n) (y|n)", line)
        if m == None:
            raise Exception('failed to parse: %s'%line)
        self.timestamp = int(m.group(1))
        self.ship = Object()
        self.ship.alive = m.group(4) == 'y';
        self.ship.position = Vector2D(float(m.group(5)), float(m.group(6)))
        if self.ship.alive:
            self.ship.velocity = Vector2D(float(m.group(7)), float(m.group(8)))
            self.ship.orientation = float(m.group(9))
        self.fortress = Object()
        self.fortress.alive = m.group(13) == 'y';
        self.fortress.position = Vector2D(355, 315)
        if self.fortress.alive:
            self.fortress.orientation = float(m.group(14))
        self.missiles = self.parse_projectiles(m.group(15))
        self.shells = self.parse_projectiles(m.group(16))
        self.points = int(m.group(18))
        self.vlner = int(m.group(21))
        self.active = m.group(33) == 'y';

class annotation():
    def __init__(self, start=None, stop=None, text=""):
        self.start = start
        self.stop = stop
        self.text = text

    def swap(self):
        (self.start, self.stop) = (self.stop, self.start)

class replay():
    def hexagon_points(self, radius):
        PointX1 = (int) (355 - radius)
        PointX2 = (int) (355 - radius * 0.5)
        PointX3 = (int) (355 + radius * 0.5)
        PointX4 = (int) (355 + radius)
        PointY1 = 315
        PointY2 = (int) (315 - radius * math.sin(math.pi*2/3))
        PointY3 = (int) (315 + radius * math.sin(math.pi*2/3))
        points = [0] * 6
        points[0] = (PointX1, PointY1)
        points[1] = (PointX2, PointY2)
        points[2] = (PointX3, PointY2)
        points[3] = (PointX4, PointY1)
        points[4] = (PointX3, PointY3)
        points[5] = (PointX2, PointY3)
        return points

    def __init__(self, preload, tagfile, subjects, subject_idx):
        self.bighex = self.hexagon_points(200)
        self.smallhex = self.hexagon_points(40)
        self.vector_explosion = pygame.image.load("gfx/exp.png").convert()
        self.vector_explosion.set_colorkey((0, 0, 0))
        self.WORLD_WIDTH = 710
        self.WORLD_HEIGHT = 626
        self.f = pygame.font.Font("fonts/freesansbold.ttf", 14)
        self.f_small = pygame.font.Font("fonts/freesansbold.ttf", 8)
        self.screen = pygame.display.get_surface()
        self.worldsurf = pygame.Surface((self.WORLD_WIDTH, self.WORLD_HEIGHT))
        self.worldrect = self.worldsurf.get_rect()
        self.worldrect.width = 410
        self.worldrect.height = 360
        self.worldrect.centerx = 1024/2
        self.worldclip = pygame.Rect(150,135,410,360)

        self.dragging = False
        self.dragging_annotation = False
        self.dragging_edge = None
        self.dragging_start_x = None

        self.speed_active = False
        self.playback_speed = 100
        self.playback_speed_text = "100"
        self.speed_rect = pygame.Rect(320, 600, 70, 40)

        self.snapshot_rect = pygame.Rect(5, 450, 1024-10, 60)
        self.play_button = button("Play", self.f, 5, 600, 100, 40)
        self.prev_ship_death_button = button("Prev Death", self.f, 110, 600, 100, 40)
        self.next_ship_death_button = button("Next Death", self.f, 215, 600, 100, 40)
        self.annotation_rect = pygame.Rect(5, 650, 385, 100)
        self.annotation_active = False
        self.annotations = []
        self.gen_score_surfs()

        self.load_predefined_tags(tagfile)

        self.subjects = subjects
        self.preload = preload
        self.gen_subject_buttons()
        self.switch_to_subject(subject_idx)

    def load_predefined_tags(self, tagfile):
        if os.path.exists(tagfile):
            print('loading tags...')
            with open(tagfile, "r") as infile:
                self.tags = [ line.strip(" \t\n") for line in infile ]
            self.gen_tag_buttons()
        else:
            self.tags = None
            self.tag_buttons = None

    def gen_tag_buttons(self):
        if self.tags == None:
            self.tag_buttons = None
        else:
            rect = pygame.Rect(5,650,380,120)
            x = rect.x
            y = rect.y
            xpad = 10
            ypad = 5
            bpad = 5
            self.tag_buttons = []
            for i in xrange(len(self.tags)):
                size = self.f.size(self.tags[i])
                b = button(self.tags[i], self.f, x, y, size[0]+xpad, size[1]+ypad)
                self.tag_buttons.append(b)
                x += size[0]+xpad+bpad
                if x > rect.right:
                    x = rect.x
                    y += size[1]+ypad+bpad

    def gen_subject_buttons(self):
        cols = 5
        w = 60
        h = 25
        pad = 5
        x = 1020 - cols * (w+pad)
        y = 760 - (h + pad) * (len(self.subjects)//cols + (0 if len(self.subjects)%cols == 0 else 1))
        i = 0
        self.subject_buttons = []
        for i in xrange(len(self.subjects)):
            c = i%cols
            r = i//cols
            b = button(subjects[i]['id'], self.f, x+c*(w+pad), y+r*(h+pad), w, h)
            self.subject_buttons.append(b)

    def gen_game_buttons(self):
        cols = 5
        w = 25
        h = 25
        pad = 5
        x = 450
        y = 600
        i = 0
        self.game_buttons = []
        for i in xrange(len(self.game_files)):
            c = i%cols
            r = i//cols
            num = os.path.splitext(os.path.basename(self.game_files[i]))[0].split('-')[2]
            b = button(num, self.f, x+c*(w+pad), y+r*(h+pad), w, h)
            self.game_buttons.append(b)

    def switch_to_subject(self, idx):
        self.current_subject = idx
        self.game_files = [ os.path.join(subjects[idx]['dir'], g) for g in subjects[idx]['games'] ]
        if self.preload:
            self.load_games_data(game_files)
        else:
            self.game_data = [ None for f in self.game_files ]
        self.gen_game_buttons()
        self.switch_to_game(0)

    def switch_to_game(self, idx):
        self.current_game = idx
        if self.game_data[idx] == None:
            self.display_progress(idx+1, len(self.game_data))
            self.game_data[idx] = self.parse_file(self.game_files[idx])
        self.snapshots = self.game_data[idx]
        self.mark_deaths()
        self.load_annotations()
        self.last_idx = None
        self.force_update = None
        self.annotation = None
        self.hover_idx = None
        self.last_frame_timestamp = pygame.time.get_ticks()
        self.playback_start_timestamp = None
        self.playing_idx = 0
        self.playing = False

    def gen_score_surfs(self):
        self.labels = ["pnts", "vlner"]
        self.label_width = 89
        self.score_y = 370
        score_width = len(self.labels)*self.label_width
        x = (1024 - score_width)/2
        self.label_surfs = []
        self.label_rects = []
        for l in self.labels:
            surf = self.f.render(l.upper(), 1, (0,255,0))
            rect = surf.get_rect()
            rect.centery = self.score_y+16
            rect.centerx = x + self.label_width/2
            self.label_surfs.append(surf)
            self.label_rects.append(rect)
            x += self.label_width

    def mark_deaths(self):
        self.ship_deaths = []
        self.fortress_deaths = []
        for s in range(0,len(self.snapshots)):
            if not self.snapshots[s].ship.alive and self.snapshots[max(0,s-1)].ship.alive:
                self.ship_deaths.append(s)
            if not self.snapshots[s].fortress.alive and self.snapshots[max(0,s-1)].fortress.alive:
                self.fortress_deaths.append(s)

    def load_games_data(self, game_files):
        self.game_data = []
        for i in xrange(len(game_files)):
            self.display_progress(i+1, len(game_files))
            self.game_data.append(self.parse_file(game_files[i]))

    def display_progress(self, n, m):
        self.screen.fill((0,0,0))
        surf = self.f.render("Loading game %d of %d ..."%(n,m), 1, (255,255,0))
        r = surf.get_rect()
        r.centerx = 1024/2
        r.centery = 768/2
        self.screen.blit(surf, r)
        pygame.display.flip()
        pygame.event.pump()

    def parse_file(self, file):
        snapshots = []
        with open(file, "r") as dat:
            for line in dat:
                if not re.match("#", line):
                    snapshots.append(snapshot(line))
        return snapshots

    # FIXME: This should be in the annotation class
    def read_from_csv(self, csv):
        x = csv.rstrip("\n").split(',')
        a = annotation(int(x[1]),int(x[3]),"\n".join(x[4].split("|")))
        return a

    def load_annotations(self):
        fname = os.path.splitext(self.game_files[self.current_game])[0] + '.tag'
        if os.path.exists(fname):
            with open(fname, 'r') as infile:
                infile.readline() # discard column headers
                self.annotations = [ self.read_from_csv(l) for l in infile ]
        else:
            self.annotations = []

    def save_annotation(self):
        if self.annotation != None:
            if self.annotation.start and self.annotation.stop and len(self.annotation.text)>0:
                self.annotations.append(self.annotation)
                self.annotation = None
                with open(os.path.splitext(self.game_files[self.current_game])[0] + '.tag', 'w') as tagfile:
                    tagfile.write("Start Timestamp, Start Frame, End Timestamp, End Frame, Annotation\n")
                    for a in sorted(self.annotations, key=lambda x: x.start):
                        tagfile.write("%s,%d,%s,%d,%s\n"%(self.format_timestamp(a.start), a.start, self.format_timestamp(a.stop), a.stop, "|".join(a.text.split("\n"))))

    def draw_hex(self, points):
        for i in range(6):
            pygame.draw.line(self.worldsurf, (0,255,0), points[i], points[(i + 1) % 6])

    def draw_explosion(self, obj):
        rect = self.vector_explosion.get_rect()
        rect.center = (obj.position.x, obj.position.y)
        self.worldsurf.blit(self.vector_explosion, rect)

    def draw_fortress(self, f):
        sinphi = math.sin(math.radians((f.orientation) % 360))
        cosphi = math.cos(math.radians((f.orientation) % 360))
        x1 = f.position.x
        y1 = f.position.y
        x2 = 36 * cosphi + f.position.x
        y2 = -(36 * sinphi) + f.position.y
        #x3, y3 = 18, -18
        x3 = 18 * cosphi - -18 * sinphi + f.position.x
        y3 = -(-18 * cosphi + 18 * sinphi) + f.position.y
        #x4, y4 = 0, -18
        x4 = -(-18 * sinphi) + f.position.x
        y4 = -(-18 * cosphi) + f.position.y
        #x5, y5 = 18, 18
        x5 = 18 * cosphi - 18 * sinphi + f.position.x
        y5 = -(18 * cosphi + 18 * sinphi) + f.position.y
        #x6, y6 = 0, 18
        x6 = - (18 * sinphi) + f.position.x
        y6 = -(18 * cosphi) + f.position.y

        pygame.draw.line(self.worldsurf, (255,255,0), (x1,y1), (x2, y2))
        pygame.draw.line(self.worldsurf, (255,255,0), (x3,y3), (x5, y5))
        pygame.draw.line(self.worldsurf, (255,255,0), (x3,y3), (x4, y4))
        pygame.draw.line(self.worldsurf, (255,255,0), (x5,y5), (x6, y6))

    def draw_ship(self, s):
        sinphi = math.sin(math.radians((s.orientation) % 360))
        cosphi = math.cos(math.radians((s.orientation) % 360))
        #old x1 = -18
        x1 = -18 * cosphi + s.position.x
        y1 = -(-18 * sinphi) + s.position.y
        #old x2 = + 18
        x2 = 18 * cosphi + s.position.x
        y2 = -(18 * sinphi) + s.position.y
        #x3 will be center point
        x3 = s.position.x
        y3 = s.position.y
        #x4, y4 = -18, 18
        x4 = -18 * cosphi - 18 * sinphi + s.position.x
        y4 = -((18 * cosphi) + (-18 * sinphi)) + s.position.y
        #x5, y5 = -18, -18
        x5 = -18 * cosphi - -18 * sinphi + s.position.x
        y5 = -((-18 * cosphi) + (-18 * sinphi)) + s.position.y

        pygame.draw.line(self.worldsurf, (255,255,0), (x1,y1), (x2,y2))
        pygame.draw.line(self.worldsurf, (255,255,0), (x3,y3), (x4,y4))
        pygame.draw.line(self.worldsurf, (255,255,0), (x3,y3), (x5,y5))

    def draw_missile(self, m):
        sinphi = math.sin(math.radians((m.orientation) % 360))
        cosphi = math.cos(math.radians((m.orientation) % 360))
        x1 = m.position.x
        y1 = m.position.y
        #x2 is -25
        x2 = -25 * cosphi + m.position.x
        y2 = -(-25 * sinphi) + m.position.y
        #x3, y3 is -5, +5
        x3 = (-5 * cosphi) - (5 * sinphi) + m.position.x
        y3 = -((5 * cosphi) + (-5 * sinphi)) + m.position.y
        #x4, y4 is -5, -5
        x4 = (-5 * cosphi) - (-5 * sinphi) + m.position.x
        y4 = -((-5 * cosphi) + (-5 * sinphi)) + m.position.y

        color = (255,255,255)
        pygame.draw.line(self.worldsurf, color, (x1, y1), (x2, y2))
        pygame.draw.line(self.worldsurf, color, (x1, y1), (x3, y3))
        pygame.draw.line(self.worldsurf, color, (x1, y1), (x4, y4))

    def draw_shell(self, s):
        sinphi = math.sin(math.radians((s.orientation) % 360))
        cosphi = math.cos(math.radians((s.orientation) % 360))

        x1 = -8 * cosphi + s.position.x
        y1 = -(-8 * sinphi) + s.position.y
        x2 = -(-6 * sinphi) + s.position.x
        y2 = -(-6 * cosphi) + s.position.y
        x3 = 16 * cosphi + s.position.x
        y3 = -(16 * sinphi) + s.position.y
        x4 = -(6 * sinphi) + s.position.x
        y4 = -(6 * cosphi) + s.position.y

        pygame.draw.line(self.worldsurf, (255,0,0), (x1, y1), (x2, y2))
        pygame.draw.line(self.worldsurf, (255,0,0), (x2, y2), (x3, y3))
        pygame.draw.line(self.worldsurf, (255,0,0), (x3, y3), (x4, y4))
        pygame.draw.line(self.worldsurf, (255,0,0), (x4, y4), (x1, y1))

    def draw_score(self, ss):
        score_width = len(self.labels)*self.label_width
        start = (1024 - score_width)/2
        end = start + score_width - 1
        pygame.draw.rect(self.screen, (0,255,0), (start, self.score_y, score_width, 63), 1)
        pygame.draw.line(self.screen, (0,255,0), (start,self.score_y+32), (end,self.score_y+32))

        values = ["%d"%ss.points, "%d"%ss.vlner]
        x = start
        h = 62
        for i in xrange(0,len(self.labels)):
            self.screen.blit(self.label_surfs[i], self.label_rects[i])
            if i < len(self.labels)-1:
                pygame.draw.line(self.screen, (0,255,0), (x+self.label_width, self.score_y), (x+self.label_width, self.score_y+h))
            surf =  self.f.render(values[i], 1, (255,255,0))
            r = surf.get_rect()
            r.centerx = x + self.label_width/2
            r.centery = self.score_y+48
            self.screen.blit(surf, r)
            x += self.label_width

    def draw_wait_for_player (self, ss):
        if not ss.active:
            surf = self.f.render('Press a key to start', 1, (255,255,255));
            r = surf.get_rect()
            r.centerx = 1024/2
            r.centery = 250
            self.screen.blit(surf, r)

    def format_timestamp(self, idx):
        ss = self.snapshots[idx]
        ms = ss.timestamp % 1000
        seconds = (ss.timestamp % 60000) // 1000
        mins = ss.timestamp // 60000
        return "%02d:%02d.%03d"%(mins, seconds, ms)

    def render_frame_info (self, idx, color):
        return self.f.render("[ %s ] F%d"%(self.format_timestamp(idx), idx), 1, color)

    def draw_frame_info (self):
        self.screen.blit(self.render_frame_info(self.playing_idx, (255,255,255)), (10, 530))
        if self.hover_idx != None:
            self.screen.blit(self.render_frame_info(self.hover_idx, (255,0,0)), (10, 550))
        if self.annotation != None:
            if self.annotation.start != None:
                self.screen.blit(self.render_frame_info(self.annotation.start,(255,255,0)), (10, 570))
            if self.annotation.stop != None:
                self.screen.blit(self.render_frame_info(self.annotation.stop,(255,255,0)), (160, 570))

    def draw_playback_speed(self):
        color = (255,255,0) if self.speed_active else (0,255,0)
        title = "Playback Speed"
        pygame.draw.rect(self.screen, color, self.speed_rect, 1)

        tsurf = self.f_small.render(title, 1, color)
        tsurf_rect = tsurf.get_rect()
        tsurf_rect.centerx = self.speed_rect.centerx
        tsurf_rect.bottom = self.speed_rect.y
        self.screen.blit(tsurf, tsurf_rect)

        surf = self.f.render(self.playback_speed_text+"%", 1, color)
        surf_rect = surf.get_rect()
        surf_rect.centerx = self.speed_rect.centerx
        surf_rect.centery = self.speed_rect.centery
        self.screen.blit(surf, surf_rect)

    def draw_snapshot(self, ss, prev_ss):
        self.worldsurf.fill((0,0,0))
        for m in ss.missiles:
            self.draw_missile(m)
        for s in ss.shells:
            self.draw_shell(s)
        pygame.draw.circle(self.worldsurf, (0,0,0), (355,315), 30)
        if ss.fortress.alive:
            self.draw_fortress(ss.fortress)
        else:
            self.draw_explosion(ss.fortress)
        if ss.ship.alive:
            self.draw_ship(ss.ship)
        else:
            self.draw_explosion(ss.ship)
        self.draw_hex(self.bighex)
        self.draw_hex(self.smallhex)
        self.screen.blit(self.worldsurf, self.worldrect, self.worldclip)
        self.draw_score(ss)
        self.draw_wait_for_player(ss)

    def quit(self):
        self.save_annotation()
        sys.exit(0)

    def update_mouse_pos(self, ev):
        #print(ev.pos)
        a = self.annotation_active
        h = self.hover_idx
        self.hover_idx = None
        # print ev.buttons

        if self.snapshot_rect.collidepoint(ev.pos):
            self.hover_idx = self.scale_to_snapshot(ev.pos[0])

        last_speed = self.speed_active
        self.speed_active =  self.speed_rect.collidepoint(ev.pos)
        if self.speed_active != last_speed:
            self.force_update = True
            if not self.speed_active:
                if len(self.playback_speed_text) > 0:
                    self.playback_speed = int(self.playback_speed_text)
                    if self.playing:
                        self.playback_start_idx = self.playing_idx
                        self.playback_start_timestamp = pygame.time.get_ticks()
                else:
                    self.playback_speed_text = "%d"%self.playback_speed

        if ev.buttons[0] == 1:
            if self.dragging:
                if self.hover_idx:
                    if not self.dragging_annotation:
                        if abs(self.dragging_start_x - ev.pos[0]) >= 5:
                            self.dragging_annotation = True
                            if self.annotation != None and self.annotation.start != None and self.annotation.stop != None:
                                # print (abs(self.dragging_start_x - self.scale_snapshot_idx(self.annotation.start)), abs(self.dragging_start_x - self.scale_snapshot_idx(self.annotation.stop)))
                                if abs(self.dragging_start_x - self.scale_snapshot_idx(self.annotation.start)) <= 10:
                                    self.dragging_edge = DRAG_START
                                elif abs(self.dragging_start_x - self.scale_snapshot_idx(self.annotation.stop)) <= 10:
                                    self.dragging_edge = DRAG_STOP
                                else:
                                    self.save_annotation()
                                    # print('discard existing. dragging new annotation', self.hover_idx)
                                    self.annotation = annotation(self.scale_to_snapshot(self.dragging_start_x), self.hover_idx)
                                    self.dragging_edge = DRAG_STOP
                            else:
                                # print('dragging new annotation', self.hover_idx)
                                self.annotation = annotation(self.scale_to_snapshot(self.dragging_start_x), self.hover_idx)
                                self.dragging_edge = DRAG_STOP
                    if self.dragging_annotation:
                        if self.dragging_edge == DRAG_STOP:
                            self.annotation.stop = self.hover_idx
                        elif self.dragging_edge == DRAG_START:
                            self.annotation.start = self.hover_idx
                        if self.annotation.start > self.annotation.stop:
                            self.annotation.swap()
                            if self.dragging_edge == DRAG_STOP:
                                self.dragging_edge = DRAG_START
                            elif self.dragging_edge == DRAG_START:
                                self.dragging_edge = DRAG_STOP
            else:
                if self.snapshot_rect.collidepoint(ev.pos):
                    self.dragging = True
                    self.dragging_start_x = ev.pos[0]

    def skip_to_death(self, direction):
        self.playing = False
        if direction == 1:
            for i in range(0,len(self.ship_deaths)):
                if self.playing_idx < self.ship_deaths[i]:
                    self.playing_idx = self.ship_deaths[i]
                    return
            self.playing_idx = 0
        else:
            for i in range(len(self.ship_deaths)-1, -1, -1):
                if self.playing_idx > self.ship_deaths[i]:
                    self.playing_idx = self.ship_deaths[i]
                    return
            if self.playing_idx > 0:
                self.playing_idx = 0
            elif len(self.ship_deaths) > 0:
                self.playing_idx = self.ship_deaths[-1]

    def toggle_playback(self):
        self.playing = not self.playing
        if self.playing:
            if self.playing_idx >= len(self.snapshots)-1:
                self.playing_idx = 0
            self.playback_start_idx = self.playing_idx
            self.playback_start_timestamp = pygame.time.get_ticks()

    def handle_mouse_click(self, ev):
        pass

    def handle_mouse_release(self, ev):
        if self.dragging:
            self.dragging = False
            self.dragging_annotation = False
            self.dragging_edge = None
            self.dragging_start_x = None
        else:
            if self.snapshot_rect.collidepoint(ev.pos):
                if ev.button == 1:
                    self.playing_idx = self.hover_idx
                    self.playing = False
                    self.force_update = True
            elif self.play_button.clicked(ev):
                self.toggle_playback()
            elif self.next_ship_death_button.clicked(ev):
                self.skip_to_death(1)
            elif self.prev_ship_death_button.clicked(ev):
                self.skip_to_death(-1)
            else:
                for i in xrange(len(self.game_buttons)):
                    if self.game_buttons[i].clicked(ev):
                        self.save_annotation()
                        self.switch_to_game(i)
                        self.force_update = True
                        return
                for i in xrange(len(self.subject_buttons)):
                    if self.subject_buttons[i].clicked(ev):
                        self.save_annotation()
                        self.switch_to_subject(i)
                        self.force_update = True
                        return
                if self.annotation and self.tag_buttons:
                    for i in xrange(len(self.tag_buttons)):
                        if self.tag_buttons[i].clicked(ev):
                            tags = self.annotation.text.split("\n")
                            if self.tags[i] in tags:
                                tags.remove(self.tags[i])
                                self.annotation.text = "\n".join(tags)
                            else:
                                self.annotation.text += "\n"+self.tags[i]
                            self.force_update = True
                            return


    def handle_key_press(self, ev):
        if ev.key == pygame.K_ESCAPE:
            if self.annotation != None:
                self.save_annotation()
                self.annotation = None
                self.force_update = True
        elif ev.key == pygame.K_LEFTBRACKET:
            if self.hover_idx != None:
                if self.annotation == None:
                    self.annotation = annotation()
                self.annotation.start = self.hover_idx
                if self.annotation.stop != None and self.annotation.start > self.annotation.stop:
                    self.annotation.swap()
                self.force_update = True
        elif ev.key == pygame.K_RIGHTBRACKET:
            if self.hover_idx != None:
                if self.annotation == None:
                    self.annotation = annotation()
                self.annotation.stop = self.hover_idx
                if self.annotation.stop != None and self.annotation.start > self.annotation.stop:
                    self.annotation.swap()
                self.force_update = True
        # elif ev.key == pygame.K_q:
        #     self.quit()
        else:
            if self.annotation != None and self.annotation.start != None and self.annotation.stop != None:
                if self.tag_buttons:
                    if (ev.key >= pygame.K_a and ev.key <= pygame.K_z) or (ev.key >= pygame.K_0 and ev.key <= pygame.K_9):
                        name = pygame.key.name(ev.key)
                        for t in self.tags:
                            if name == t[0]:
                                tags = self.annotation.text.split("\n")
                                if t in tags:
                                    tags.remove(t)
                                    self.annotation.text = "\n".join(tags)
                                else:
                                    self.annotation.text += "\n"+t
                                self.force_update = True
                                break
                else:
                    if (ev.key >= pygame.K_a and ev.key <= pygame.K_z) or (ev.key >= pygame.K_0 and ev.key <= pygame.K_9):
                        self.annotation.text += pygame.key.name(ev.key)
                        self.force_update = True
                    elif ev.key == pygame.K_SPACE:
                        self.annotation.text += " "
                        self.force_update = True
                    elif ev.key == pygame.K_BACKSPACE:
                        self.annotation.text = self.annotation.text[:-1]
                        self.force_update = True
                    elif ev.key == pygame.K_RETURN:
                        self.annotation.text += "\n"
                        self.force_update = True
            elif self.speed_active:
                if ev.key >= pygame.K_0 and ev.key <= pygame.K_9:
                    self.playback_speed_text += pygame.key.name(ev.key)
                    self.force_update = True
                elif ev.key == pygame.K_BACKSPACE:
                    self.playback_speed_text = self.playback_speed_text[:-1]
                    self.force_update = True
            else:
                if ev.key == pygame.K_e:
                    if self.hover_idx != None:
                        self.playing = False
                        self.save_annotation()
                        for a in self.annotations:
                            if self.hover_idx >= a.start and self.hover_idx <= a.stop:
                                self.annotation = a
                                self.annotations.remove(a)
                                self.force_update = True
                                break
                elif ev.key == pygame.K_SPACE:
                    self.toggle_playback()
                    self.last_frame_timestamp = pygame.time.get_ticks()
                elif ev.key == pygame.K_p:
                    self.skip_to_death(-1)
                elif ev.key == pygame.K_n:
                    self.skip_to_death(1)

    def process_events(self):
        # try not to take up extra processor time.
        events = []
        if pygame.event.peek((pygame.QUIT,pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN)):
            events = pygame.event.get()
        elif not self.playing:
            e = pygame.event.wait()
            events = [e]
            events.extend(pygame.event.get())
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                self.handle_key_press(ev)
            elif ev.type == pygame.MOUSEMOTION:
                self.update_mouse_pos(ev)
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(ev)
            elif ev.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_release(ev)
            elif ev.type == pygame.QUIT:
                self.quit()

    def scale_snapshot_idx(self,i):
        return int(self.snapshot_rect.x + i/float(len(self.snapshots))*self.snapshot_rect.width)

    def scale_to_snapshot(self, x):
        return min(int((x-self.snapshot_rect.x) / float(self.snapshot_rect.width) * len(self.snapshots)),
                   len(self.snapshots)-1)

    def draw_annotation_text(self, a, active):
        if active:
            acolor = (255,255,0)
        else:
            acolor = (0,255,0)
        if self.tag_buttons:
            tags = a.text.split("\n")
            # print(tags)
            for i in xrange(len(self.tag_buttons)):
                self.tag_buttons[i].draw(self.screen, self.tags[i] in tags)
        else:
            pygame.draw.rect(self.screen, acolor, self.annotation_rect, 1)
            x = self.annotation_rect.left + 5
            y = self.annotation_rect.top + 5
            fh = self.f.get_height()
            for line in a.text.split("\n"):
                self.screen.blit(self.f.render(line, 1, acolor), (x,y))
                y += fh

    def draw_screen(self, idx):
        self.screen.fill((0,0,0))
        self.draw_snapshot(self.snapshots[idx], self.snapshots[idx-1])
        pygame.draw.rect(self.screen, (0,255,0), self.snapshot_rect, 1)
        self.draw_frame_info()
        for d in self.ship_deaths:
            x = self.scale_snapshot_idx(d)
            pygame.draw.line(self.screen, (100,100,100), (x, self.snapshot_rect.top+1), (x, self.snapshot_rect.bottom-2))
        for d in self.fortress_deaths:
            x = self.scale_snapshot_idx(d)
            pygame.draw.line(self.screen, (255,50,50), (x, self.snapshot_rect.top+1), (x, self.snapshot_rect.bottom-2))
        if self.hover_idx != None:
            hover_x = self.scale_snapshot_idx(self.hover_idx)
            pygame.draw.line(self.screen, (255,0,0), (hover_x, self.snapshot_rect.top+1), (hover_x, self.snapshot_rect.bottom-1))
        playing_x = self.scale_snapshot_idx(self.playing_idx)
        pygame.draw.line(self.screen, (255,255,255), (playing_x, self.snapshot_rect.top), (playing_x, self.snapshot_rect.bottom-1))
        self.play_button.draw(self.screen)
        self.next_ship_death_button.draw(self.screen)
        self.prev_ship_death_button.draw(self.screen)
        for i in xrange(len(self.game_buttons)):
            self.game_buttons[i].draw(self.screen, i == self.current_game)

        for i in xrange(len(self.subject_buttons)):
            self.subject_buttons[i].draw(self.screen, i == self.current_subject)

        for a in self.annotations:
            start = self.scale_snapshot_idx(a.start)
            stop = self.scale_snapshot_idx(a.stop)
            pygame.draw.rect(self.screen, (50,50,200), (start, self.snapshot_rect.bottom+3, stop-start+1, 5), 0)

        if self.annotation == None:
            if self.hover_idx != None:
                idx = self.hover_idx
            else:
                idx = self.playing_idx
            for a in self.annotations:
                if idx >= a.start and idx <= a.stop:
                    self.draw_annotation_text(a, False)
                    break
        else:
            if self.annotation.start != None:
                start_x = self.scale_snapshot_idx(self.annotation.start)
                pygame.draw.lines(self.screen, (255,255,0), False, ((start_x+3, self.snapshot_rect.top-2), (start_x, self.snapshot_rect.top-2), (start_x, self.snapshot_rect.bottom+2), (start_x+3, self.snapshot_rect.bottom+2)))
            if self.annotation.stop != None:
                stop_x = self.scale_snapshot_idx(self.annotation.stop)
                pygame.draw.lines(self.screen, (255,255,0), False, ((stop_x-3, self.snapshot_rect.top-2), (stop_x, self.snapshot_rect.top-2), (stop_x, self.snapshot_rect.bottom+2), (stop_x-3, self.snapshot_rect.bottom+2)))
            # self.draw_annotation_text(self.annotation, self.annotation_active)
            self.draw_annotation_text(self.annotation, False)

        self.draw_playback_speed()

        pygame.display.flip()

    def main_loop(self):
        self.draw_screen(0)
        while True:
            self.process_events()
            pygame.event.pump()
            now = pygame.time.get_ticks()
            if self.playing:
                diff = self.snapshots[min(len(self.snapshots)-1,self.playing_idx+1)].timestamp - self.snapshots[self.playback_start_idx].timestamp
                actual = (now - self.playback_start_timestamp) * self.playback_speed / 100
                if actual >= diff:
                    ss_sum = 0
                    # print('actual',actual)
                    start_timestamp = self.snapshots[self.playback_start_idx].timestamp
                    while self.playing_idx < len(self.snapshots)-1:
                        if self.snapshots[self.playing_idx].timestamp - start_timestamp < actual:
                            self.playing_idx += 1
                        else:
                            self.playing_idx -= 1
                            break
                    if self.hover_idx != None:
                        self.force_update = True
                    if self.playing_idx >= len(self.snapshots)-1:
                        self.playing_idx = len(self.snapshots)-1
                        self.playing = False
            if self.hover_idx != None:
                idx = self.hover_idx
            else:
                idx = self.playing_idx
            if self.force_update or idx != self.last_idx:
                self.force_update = False
                self.last_idx = idx
                self.draw_screen(idx)
            else:
                if self.playing:
                    diff = self.snapshots[min(len(self.snapshots)-1,self.playing_idx+1)].timestamp - self.snapshots[self.playback_start_idx].timestamp
                    actual = (pygame.time.get_ticks() - self.playback_start_timestamp) * self.playback_speed / 100
                    remaining = int(diff - actual)
                    if remaining > 0:
                        pygame.time.wait(min(3,remaining))

def read_subject_list(datadir):
    subjects = []
    for root, dirs, files in os.walk(datadir,topdown=False):
        (head,tail) = os.path.split(root)
        games = []
        for f in files:
            if re.match('(:?\w|\d)+-\d+-\d+\.dat$', f):
                games.append(f)
        if len(games) > 0:
            subjects.append({'id': tail, 'dir': root, 'games': sorted(games, key=lambda f: int(os.path.splitext(f)[0].split('-')[2]))})
    return subjects

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data',metavar='DIR',help="Specify the data directory from which to load subject data",default="../data/")
    parser.add_argument('--id',help="The subject ID to use when loading game data")
    parser.add_argument('--file',help="Explicitely specify the game data file to load")
    parser.add_argument('--tagfile',metavar="FILE",default="../replay-tags.txt",help="Specify a file containing predefined tags")
    parser.add_argument('--preload', help="Preload all game data (may be slow)", action='store_true')
    fixed_argv = [a for a in sys.argv[1:] if not re.match('-psn(?:_\d+)+$', a)]
    args = parser.parse_args(fixed_argv)

    pygame.init()
    pygame.display.set_mode((1024, 768))

    if args.file != None:
        tmp = os.path.split(args.file)
        subjects = [{'id': 'file', 'dir': tmp[0], 'games': [tmp[1]]}]
        subject_idx = 0
    else:
        if not os.path.exists(args.data):
            raise Exception('Data directory %s doesn''t exist!'%args.data)

        screen = pygame.display.get_surface()
        font = pygame.font.Font("fonts/freesansbold.ttf", 32)

        subjects = read_subject_list(args.data)
        ids = [ s['id'] for s in subjects ]

        if args.id == None:
            subject_idx = sfdialog.choose_from_list("Choose Subject", screen, font, ids)
            if subject_idx == None:
                sys.exit(0)
        else:
            if args.id not in ids:
                raise Exception('Cannot find subject ID %s'%args.id)
            subject_idx = ids.index(args.id)

    r = replay(args.preload, args.tagfile, subjects, subject_idx)
    r.main_loop()
