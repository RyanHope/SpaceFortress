import os
import sys
import re
import argparse
import openpyxl as xl

class analysis():
    def __init__(self, datadir):
        self.subjects = self.read_subject_list(datadir)

    def session_number (self, session_file):
        return int(os.path.splitext(session_file)[0].split('-')[1])

    def read_subject_list(self, datadir):
        subjects = []
        for root, dirs, files in os.walk(datadir,topdown=False):
            (head,tail) = os.path.split(root)
            sessions = []
            for f in files:
                if re.match('(:?\w|\d)+-\d+\.dat$', f):
                    sessions.append(f)
            if len(sessions) > 0:
                s = {'id': tail, 'dir': root, 'sessions': sorted(sessions, key=lambda f: self.session_number(f))}
                subjects.append(s)
        return subjects

    def parse_dictionary(self, d):
        ret = {}
        start = 0
        p1 = re.compile('((?:\w|-)+)="(.*?(?:\\..*?)*)"')
        p2 = re.compile('((?:\w|-)+)=([^\\\ ]*(?:\\\.[^\\\ ]*)*)')
        while start < len(d):
            # print start, d
            m = p1.match(d, start) or p2.match(d, start)
            if m:
                start = m.end()+1
                ret[m.group(1)] = re.sub('\\\ |(?:\\\\n)+', ' ', m.group(2))
                # print '"%s"'%m.group(0)
            else:
                raise Exception('failed to parse %s'%d[start:])
        # print ret
        return ret

    def parse_session(self, session_file):
        lines = []
        with open(session_file) as infile:
            for l in infile:
                m = re.match('(\d+\.\d+) (\d+|-) ((?:\w|-)+) ((?:\w|-)+) (.*)$', l)
                if m:
                    line = {'timestamp': m.group(1),
                            'index': m.group(2),
                            'screen': m.group(3),
                            'tag': m.group(4),
                            'data': self.parse_dictionary(m.group(5))}
                    lines.append(line)
                else:
                    raise Exception('cannot parse session file')
        return lines

    def dump_protocol(self, ws, subject, session, lines):
        c = 1
        for l in lines:
            if l['screen'] == 'questionnaire' and l['tag'] == 'end':
                ws.append([subject, session, c, l['data']['shoot'], l['data']['turn'], l['data']['thrust'], l['data']['strategy'], l['data']['thoughts']])
                c += 1

    def dump(self, outfile):
        wb = xl.Workbook()
        ws = wb.active
        ws.title = "Protocol"
        ws.append(['Subject', 'Session', 'Num', 'Shoot', 'Turn', 'Thrust', 'Strategy', 'Thoughts'])
        for s in self.subjects:
            print 'Dumping "%s"'%s['id']
            for session in s['sessions']:
                self.dump_protocol(ws, s['id'], self.session_number(session), self.parse_session(os.path.join(s['dir'], session)))
                ws.append([])
        wb.save(outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', metavar="DIR", default='../data/', help="specify data dir")
    parser.add_argument('--output-file', metavar="FILE", default='protocol.xlsx', help="specify output file")
    args = parser.parse_args()

    a = analysis(args.data)
    a.dump(os.path.join(args.data, args.output_file))
