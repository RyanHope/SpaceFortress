#!/usr/bin/env python

import os
import sys
import re
import argparse
import openpyxl as xl

class subject(object):
    def __init__(self, datadir, id):
        self.id = id
        self.datadir = datadir


class analysis(object):
    def __init__(self, datadir, output_file):
        self.datadir = datadir
        self.output_file = output_file

    def update(self, msg):
        print(msg)

    def scan_and_dump(self):
        self.update('Scanning %s'%os.path.abspath(self.datadir))
        if not os.path.exists(self.datadir):
            self.update('Folder does not exist! Abort.')
        else:
            self.subjects = self.read_subject_list()
            for s in self.subjects:
                self.update('%s games=%d'%(s['id'], len(s['games'])))
            self.update('Dumping to %s'%os.path.abspath(os.path.join(self.datadir, self.output_file)))
            self.dump(self.output_file)
            self.update('Done.')

    def read_subject_list(self):
        subjects = []
        for root, dirs, files in os.walk(self.datadir,topdown=False):
            (head,tail) = os.path.split(root)
            games = []
            for f in files:
                if re.match('(:?\w|\d)+-\d+-\d+\.evt$', f):
                    games.append(f)
            if len(games) > 0:
                s = {'id': tail, 'dir': root, 'games': sorted(games, key=lambda f: int(os.path.splitext(f)[0].split('-')[2]))}
                subjects.append(s)
        return subjects

    @staticmethod
    def parse_events(evt_file):
        events = []
        c = 0
        with open(evt_file) as infile:
            for l in infile:
                c += 1
                m = re.match('^(\d+) (\d+\.\d+) (.*)$', l)
                if not m:
                    raise Exception('%s:%d:error parsing event file'%(evt_file, c))
                events.append({'ts': m.group(1), 'tags': m.group(3).split(',')})
        return events

    @staticmethod
    def parse_game_file(evt_file):
        (root, ext) = os.path.splitext(evt_file)
        gfile = root + '.dat'
        with open(gfile) as infile:
            features = {'total': None,
                        'points': None,
                        'raw': None,
                        'bonus': None}
            for l in infile:
                p = re.match('^# pnts score (-?\d+)', l)
                t = re.match('^# total score (-?\d+)', l)
                r = re.match('^# raw pnts (-?\d+)', l)
                b = re.match('^# bonus earned \$(\d+\.\d+)', l)
                if p:
                    features['points'] = int(p.group(1))
                elif t:
                    features['total'] = int(t.group(1))
                elif r:
                    features['raw'] = int(r.group(1))
                elif b:
                    features['bonus'] = float(b.group(1))
        return features

    @staticmethod
    def count_tag (events, tag):
        c = 0
        for e in events:
            if tag in e['tags']:
                c += 1
        return c

    @staticmethod
    def count_tag_except (events, tag, exception):
        c = 0
        for e in events:
            if tag in e['tags'] and exception not in e['tags']:
                c += 1
        return c

    def dump_game_events(self, ws, s):
        ws.append(['Subject', 'Session', 'Game', 'Game Type', 'Fortress Kills', 'Fortress Hits', 'Fortress Fired', 'Missiles Fired', 'Vlner Reset', 'Hit By Shell', 'Hit Small Hex', 'Hit Big Hex', 'Raw Points', 'Points', 'Bonus'])
        gnum = 1
        for gf in s['games']:
            events = analysis.parse_events(os.path.join(self.datadir, s['id'], gf))
            score = analysis.parse_game_file(os.path.join(self.datadir, s['id'], gf))
            ws.append([s['id'],
                       1,
                       gnum,
                       'fortress',
                       analysis.count_tag(events, 'fortress-destroyed'),
                       analysis.count_tag(events, 'hit-fortress'),
                       analysis.count_tag(events, 'fortress-fired'),
                       analysis.count_tag(events, 'missile-fired'),
                       analysis.count_tag_except(events, 'vlner-reset', 'fortress-destroyed'),
                       analysis.count_tag(events, 'shell-hit-ship'),
                       analysis.count_tag(events, 'explode-smallhex'),
                       analysis.count_tag(events, 'explode-bighex'),
                       score['raw'],
                       score['points'],
                       int(score['bonus']*100)])
            gnum += 1

    def dump(self, outfile):
        wb = xl.Workbook()
        ws = None
        for s in self.subjects:
            if ws == None:
                ws = wb.active
            else:
                ws = wb.create_sheet()
            ws.title = s['id']
            self.dump_game_events(ws, s)
        wb.save(os.path.join(self.datadir, outfile))

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--data',metavar='DIR',help="Specify the data directory from which to load subject data",default="../../../data/")
#     parser.add_argument('--output-file',metavar='FILE',help="Specify the name of the output file (excel)",default="game-events.xlsx")
#     fixed_argv = [a for a in sys.argv[1:] if not re.match('-psn(?:_\d+)+$', a)]
#     args = parser.parse_args(fixed_argv)

#     if not os.path.exists(args.data):
#         raise Exception('Data directory %s doesn''t exist!'%args.data)

#     print 'Scanning %s...'%args.data
#     a = analysis(args.data)
#     for s in a.subjects:
#         print s['id'], 'games =', len(s['games'])
#     print('Dumping to %s'%os.path.join(args.data, args.output_file))
#     a.dump(args.output_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', metavar="DIR", default='../data/', help="specify data dir")
    parser.add_argument('--output-file', metavar="FILE", default='game-events.xlsx', help="specify output file")
    args = parser.parse_args()

    a = analysis(args.data, args.output_file)
    a.scan_and_dump()
